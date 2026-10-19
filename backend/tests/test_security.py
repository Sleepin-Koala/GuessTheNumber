"""Attaques qui doivent echouer: usurpation, acces sans jeton, detournement de sockets, abus de debit."""
import hashlib
import time

import pytest
import re
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import all as A
from conftest import give, secret, db
from main import app
from routes.auth import PUBLIC
from routes.game_mode import duel_mode as D
from security import limiter, DEFAULT_RULES, MAX_BODY
from test_duel import host, join, hide, new_player, status, coins

pytestmark = pytest.mark.timeout(30)
JSON = {"Content-Type": "application/json"}


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def anon():
    return TestClient(app)          # sans jeton, sans lifespan: suffisant pour du HTTP


@pytest.fixture()
def two(client):
    """(victime, attaquant): id + jeton de chacun."""
    def make():
        r = client.post("/user/new_player").json()
        return r["id"], r["token"]
    return make(), make()


@pytest.fixture()
def rate_limited():
    limiter.enabled = True
    limiter.hits.clear()
    yield limiter
    limiter.enabled = False
    limiter.rules = DEFAULT_RULES
    limiter.hits.clear()


# ------------------------------------------------------------------ acces par defaut refuse
def _api_routes():
    """Toutes les routes HTTP, lues dans le schema OpenAPI (fiable quelle que soit la facon dont FastAPI assemble les routeurs)."""
    for path, ops in app.openapi()["paths"].items():
        for method in ops:
            if (method.upper(), path) not in PUBLIC:
                yield method.upper(), path


def test_every_non_public_route_refuses_requests_without_a_token(anon):
    checked = 0
    for method, path in _api_routes():
        url = re.sub(r"\{[^}]+\}", "x", path)
        r = anon.request(method, url, json={} if method == "POST" else None)
        assert r.status_code == 401, f"{method} {path} answered {r.status_code} without a token"
        checked += 1
    assert checked >= 24, "the route sweep should cover the whole API"


@pytest.mark.parametrize("header", ["Bearer nonsense", "Basic dXNlcjpwYXNz", "Bearer ", "bearer", "Token abc", "Bearer " + "a" * 500])
def test_bad_authorization_headers_are_refused(anon, header):
    assert anon.get("/user/me", headers={"Authorization": header}).status_code == 401


def test_public_routes_stay_public(anon):
    assert anon.get("/health").status_code == 200
    assert anon.post("/user/new_player").status_code == 200


def test_the_old_get_new_player_no_longer_creates_accounts(anon):
    assert anon.get("/user/new_player").status_code in (401, 405, 403)


# ------------------------------------------------------------------ usurpation
def test_cannot_read_someone_elses_account(client, two):
    (victim, _), (_, attacker_token) = two
    for path in (f"/user/{victim}", f"/user/stats/{victim}", f"/user/stats/history/{victim}", f"/shop/inventory/{victim}"):
        assert client.get(path, headers=bearer(attacker_token)).status_code == 403, path


def test_cannot_act_in_someone_elses_name(client, two):
    (victim, vt), (attacker, at) = two
    give(victim, 3)
    s = client.post("/game/classic/level", json={"level": 1, "player_id": victim}, headers=bearer(vt)).json()
    sid = s["session_id"]
    A_ = bearer(at)
    attempts = [
        ("/game/guess", {"session_id": sid, "player_id": victim, "number": 1}),
        ("/game/powerup", {"session_id": sid, "player_id": victim, "item_id": 3}),
        ("/game/classic/level", {"level": 1, "player_id": victim}),
        ("/game/classic/end_level", {"session_id": sid, "player_id": victim, "status": "lose", "level_played": 1, "ended": 0}),
        ("/game/discovery/start", {"player_id": victim, "max_range": 10}),
        ("/game/endless/start", {"player_id": victim, "bet": 100, "stage": 1}),
        ("/shop/buy", {"playerId": victim, "itemId": 3}),
        ("/shop/count", {"playerId": victim, "itemId": 3}),
        ("/user/rename", {"player_id": victim, "name": "pwned"}),
        ("/game/duel/host", {"host_id": victim, "name": "x", "amount": 0, "max_range": 10}),
    ]
    for path, body in attempts:
        r = client.post(path, json=body, headers=A_)
        assert r.status_code == 403, f"{path} -> {r.status_code}"
    victim_now = client.get("/user/me", headers=bearer(vt)).json()
    assert victim_now["coins"] == 500 and victim_now["name"] != "pwned"      # nothing moved
    assert client.get(f"/shop/inventory/{victim}", headers=bearer(vt)).json()["items"] == {"3": 1}


def test_cannot_hijack_a_duel_by_naming_the_other_player(client, two):
    (hider, ht), (attacker, at) = two
    rid = host(client, hider, bet=0, rng=20)["room_id"]
    assert client.post("/game/duel/join", json={"player_id": attacker, "room_id": rid}, headers=bearer(at)).status_code == 200
    # the attacker is the guest: they try to hide a number "as" the host, to forfeit the host, to cancel the room
    for path, body in [(f"/game/duel/rooms/{rid}/hide", {"player_id": hider, "number": 5}),
                       (f"/game/duel/rooms/{rid}/forfeit", {"player_id": hider}),
                       (f"/game/duel/rooms/{rid}/leave", {"player_id": hider})]:
        assert client.post(path, json=body, headers=bearer(at)).status_code == 403, path
    with db() as s:
        s.expire_all()
        room = s.query(A.Duel).filter_by(id=rid).first()
        assert room.hider_number is None and room.status == "round1_hide"
    # a real member of the room can still play
    assert client.post(f"/game/duel/rooms/{rid}/hide", json={"player_id": hider, "number": 5}, headers=bearer(ht)).status_code == 200


def test_a_third_party_cannot_join_as_someone_else(client, two):
    (victim, _), (_, at) = two
    h = new_player(client)
    rid = host(client, h)["room_id"]
    assert client.post("/game/duel/join", json={"player_id": victim, "room_id": rid}, headers=bearer(at)).status_code == 403
    assert status(client, rid)["status"] == "waiting"


# ------------------------------------------------------------------ jetons
def test_the_server_stores_only_a_hash_of_the_token(client):
    r = client.post("/user/new_player").json()
    with db() as s:
        row = s.query(A.Player).filter_by(id=r["id"]).first()
        stored, name, pid = row.token_hash, row.name, row.id
    assert stored == hashlib.sha256(r["token"].encode()).hexdigest()
    assert r["token"] not in (stored, name, pid) and len(r["token"]) >= 40


def test_tokens_are_never_repeated_by_other_endpoints(client):
    r = client.post("/user/new_player").json()
    me = client.get("/user/me", headers=bearer(r["token"])).json()
    assert "token" not in me and me["id"] == r["id"]
    assert "token" not in client.get(f"/user/{r['id']}", headers=bearer(r["token"])).json()
    rid = host(client, r["id"])["room_id"]
    assert r["token"] not in str(status(client, rid)) and r["token"] not in str(client.get("/game/duel/rooms").json())


def test_two_accounts_never_share_a_token(client):
    tokens = {client.post("/user/new_player").json()["token"] for _ in range(20)}
    assert len(tokens) == 20


def test_legacy_accounts_can_claim_a_token_exactly_once(client, anon):
    legacy = A.Player(id="legacy-1", name="old", level=1, created_at=time.time(), xp=0, coins=500, gems=5)
    with db() as s:
        s.add(legacy)
    r = anon.post("/user/claim", json={"player_id": "legacy-1"})
    assert r.status_code == 200 and anon.get("/user/me", headers=bearer(r.json()["token"])).json()["id"] == "legacy-1"
    assert anon.post("/user/claim", json={"player_id": "legacy-1"}).status_code == 409        # closed after the first claim
    modern = client.post("/user/new_player").json()["id"]
    assert anon.post("/user/claim", json={"player_id": modern}).status_code == 409           # tokenised accounts cannot be claimed
    assert anon.post("/user/claim", json={"player_id": "nope"}).status_code == 409            # no hint whether an id exists


# ------------------------------------------------------------------ limitation de debit
def test_account_creation_is_rate_limited(anon, rate_limited):
    codes = [anon.post("/user/new_player").status_code for _ in range(12)]
    assert codes[:10] == [200] * 10 and codes[10] == 429
    r = anon.post("/user/new_player")
    assert r.status_code == 429 and int(r.headers["retry-after"]) >= 1 and "detail" in r.json()


def test_guess_limit_is_per_player_not_global(client, two, rate_limited):
    (a, ta), (b, tb) = two
    rate_limited.rules = [("POST", r"^/game/guess$", 3, 60, "token"), ("*", r".*", 10_000, 60, "ip")]
    sa = client.post("/game/discovery/start", json={"player_id": a, "max_range": 50}, headers=bearer(ta)).json()["session_id"]
    sb = client.post("/game/discovery/start", json={"player_id": b, "max_range": 50}, headers=bearer(tb)).json()["session_id"]
    g = lambda pid, tok, sid: client.post("/game/guess", json={"session_id": sid, "player_id": pid, "number": 1}, headers=bearer(tok)).status_code
    assert [g(a, ta, sa) for _ in range(4)] == [200, 200, 200, 429]
    assert g(b, tb, sb) == 200                                   # the other player is unaffected


def test_oversized_bodies_are_rejected(anon):
    r = anon.post("/user/claim", content=b"x" * (MAX_BODY + 1), headers=JSON)
    assert r.status_code == 413


# ------------------------------------------------------------------ navigateur: en-tetes et CORS
def test_security_headers_are_on_every_answer(client, anon):
    for r in (anon.get("/health"), anon.get("/user/me"), client.get("/user/me", headers=bearer(client.default))):
        assert r.headers["x-content-type-options"] == "nosniff"
        assert r.headers["x-frame-options"] == "DENY" and r.headers["referrer-policy"] == "no-referrer"
        assert r.headers["cache-control"] == "no-store"


def test_cors_only_allows_known_origins_and_no_credentials(anon):
    ok = anon.options("/user/new_player", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization,content-type"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-credentials" not in ok.headers
    evil = anon.options("/user/new_player", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in evil.headers
    assert "https://evil.example" not in anon.get("/health", headers={"Origin": "https://evil.example"}).headers.get("access-control-allow-origin", "")
    # the page must be able to read Retry-After on a 429 (otherwise it cannot tell the player how long to wait)
    assert "retry-after" in anon.get("/health", headers={"Origin": "http://localhost:5173"}).headers["access-control-expose-headers"].lower()


# ------------------------------------------------------------------ entrees
@pytest.mark.parametrize("body", [
    {"number": 10 ** 30}, {"number": -10 ** 30}, {"number": "abc"}, {"number": None}, {"number": 1.5e300},
])
def test_absurd_numbers_get_a_422_never_a_500(client, body):
    pid = new_player(client)
    sid = client.post("/game/discovery/start", json={"player_id": pid, "max_range": 10}).json()["session_id"]
    r = client.post("/game/guess", json={"session_id": sid, "player_id": pid, **body})
    assert r.status_code == 422


def test_other_oversized_inputs_are_refused(client):
    pid = new_player(client)
    assert client.post("/user/rename", json={"player_id": pid, "name": "x" * 500}).status_code == 422
    assert client.post("/game/discovery/start", json={"player_id": "p" * 1000, "max_range": 10}).status_code == 422
    assert client.post("/game/endless/start", json={"player_id": pid, "bet": 10 ** 30, "stage": 1}).status_code == 422
    assert client.post("/game/duel/host", json={"host_id": pid, "name": "n" * 500, "amount": 0, "max_range": 10}).status_code == 422
    assert client.post("/shop/buy", json={"playerId": pid, "itemId": 10 ** 30}).status_code == 422


# ------------------------------------------------------------------ WebSockets
def ws_fails(client, url, code, **kw):
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect(url, **kw):
            pass
    assert e.value.code == code


def test_sockets_need_a_valid_token_in_the_subprotocol(client, two):
    (hid, ht), (aid, at) = two
    rid = host(client, hid)["room_id"]
    url = f"/game/duel/ws/{rid}"
    ws_fails(client, url, 4401, subprotocols=[])                                # no token
    ws_fails(client, url, 4401, subprotocols=["gtn.v1", "garbage"])
    ws_fails(client, url, 4401, subprotocols=["other", ht])                     # wrong protocol name
    ws_fails(client, f"{url}?token={ht}", 4401, subprotocols=[])                # a token in the URL is ignored
    ws_fails(client, "/game/duel/ws-lobby", 4401, subprotocols=[])
    with client.websocket_connect(url, subprotocols=["gtn.v1", ht]) as ws:
        assert ws.accepted_subprotocol == "gtn.v1" and ws.receive_json()["room"]["room_id"] == rid


def test_socket_identity_comes_from_the_token_not_from_the_url(client, two):
    (hid, ht), (aid, at) = two
    rid = host(client, hid)["room_id"]
    ws_fails(client, f"/game/duel/ws/{rid}?player_id={hid}", 4403, subprotocols=["gtn.v1", at])   # attacker names the host: still refused


def test_sockets_from_unknown_websites_are_refused(client, two):
    (hid, ht), _ = two
    rid = host(client, hid)["room_id"]
    ws_fails(client, f"/game/duel/ws/{rid}", 4403, subprotocols=["gtn.v1", ht], headers={"Origin": "https://evil.example"})
    with client.websocket_connect(f"/game/duel/ws/{rid}", subprotocols=["gtn.v1", ht], headers={"Origin": "http://localhost:5173"}) as ws:
        assert ws.receive_json()["type"] == "room"


def test_connections_per_address_are_capped(client, two, monkeypatch):
    (hid, ht), _ = two
    rid = host(client, hid)["room_id"]
    monkeypatch.setattr(D, "MAX_WS_PER_IP", 2)
    with client.websocket_connect(f"/game/duel/ws/{rid}", subprotocols=["gtn.v1", ht]) as w1, \
         client.websocket_connect("/game/duel/ws-lobby", subprotocols=["gtn.v1", ht]) as w2:
        w1.receive_json(); w2.receive_json()
        ws_fails(client, "/game/duel/ws-lobby", 4429, subprotocols=["gtn.v1", ht])


# ------------------------------------------------------------------ adresse du client derriere un proxy
def _scope(xff=None, peer="10.0.0.1"):
    headers = [(b"x-forwarded-for", xff.encode())] if xff else []
    return {"headers": headers, "client": (peer, 1234)}


def test_client_ip_ignores_forwarded_headers_unless_a_proxy_is_trusted(monkeypatch):
    import security
    monkeypatch.setattr(security, "TRUST_PROXY", False)
    assert security.client_ip(_scope("6.6.6.6", peer="10.0.0.1")) == "10.0.0.1"


def test_client_ip_cannot_be_spoofed_through_the_start_of_x_forwarded_for(monkeypatch):
    import security
    monkeypatch.setattr(security, "TRUST_PROXY", True)
    monkeypatch.setattr(security, "PROXY_HOPS", 1)
    # an attacker prepends a fake address; the trusted proxy appends the real one at the end
    assert security.client_ip(_scope("6.6.6.6, 203.0.113.9")) == "203.0.113.9"
    assert security.client_ip(_scope("203.0.113.9")) == "203.0.113.9"
    assert security.client_ip(_scope(None, peer="10.0.0.1")) == "10.0.0.1"          # header missing: fall back to the peer
    monkeypatch.setattr(security, "PROXY_HOPS", 2)                                # two trusted proxies in front
    assert security.client_ip(_scope("6.6.6.6, 203.0.113.9, 172.16.0.5")) == "203.0.113.9"


def test_the_database_location_comes_from_the_environment(tmp_path, monkeypatch):
    import database
    target = tmp_path / "volume" / "x.db"
    target.parent.mkdir()
    monkeypatch.delenv("GTN_DATABASE_URL", raising=False)     # (un lancement sur Postgres le definit)
    monkeypatch.setenv("GTN_DB_PATH", str(target))
    database.make_db()
    assert target.exists() and target.stat().st_size > 0


@pytest.mark.parametrize("given,expected", [
    ("postgres://u:p@host/db", "postgresql+psycopg://u:p@host/db"),                            # forme donnee par certains hebergeurs
    ("postgresql://u:p@host/db?sslmode=require", "postgresql+psycopg://u:p@host/db?sslmode=require"),   # forme donnee par Neon
    ("postgresql+psycopg://u:p@host/db", "postgresql+psycopg://u:p@host/db"),                 # deja complete: inchangee
    ("sqlite:///autre.db", "sqlite:///autre.db"),
])
def test_database_urls_are_normalised_for_the_postgres_driver(monkeypatch, given, expected):
    import database
    monkeypatch.setenv("GTN_DATABASE_URL", given)
    assert database.database_url() == expected


def test_the_url_wins_over_the_sqlite_path_and_the_default_is_a_local_file(monkeypatch):
    import database
    monkeypatch.delenv("GTN_DATABASE_URL", raising=False)
    monkeypatch.delenv("GTN_DB_PATH", raising=False)
    assert database.database_url() == "sqlite:///main.db"
    monkeypatch.setenv("GTN_DB_PATH", "/data/main.db")
    assert database.database_url() == "sqlite:////data/main.db"
    monkeypatch.setenv("GTN_DATABASE_URL", "postgres://u:p@h/d")
    assert database.database_url().startswith("postgresql+psycopg://")


def test_money_columns_hold_more_than_a_32_bit_integer(client):
    """Postgres limite un Integer a ~2,1 milliards: les pieces / mises doivent etre en 64 bits."""
    pid = new_player(client)
    with db() as s:
        s.query(A.Player).filter_by(id=pid).first().coins = 5 * 10 ** 12
    assert client.get("/user/me").json()["coins"] == 5 * 10 ** 12


def test_endless_rewards_are_capped_so_nothing_can_overflow():
    import engine
    assert engine.EndlessMode.getRoundReward(100, 10 ** 9) == engine.MAX_REWARD
    assert engine.EndlessMode.getRoundReward(3, 100) == 195


def test_whoami_reports_the_address_the_server_sees(anon, monkeypatch):
    import security
    r = anon.get("/whoami")
    assert r.status_code == 200 and r.json()["ip"] == "testclient"
    monkeypatch.setattr(security, "TRUST_PROXY", True)
    monkeypatch.setattr(security, "PROXY_HOPS", 1)
    assert anon.get("/whoami", headers={"X-Forwarded-For": "6.6.6.6, 203.0.113.7"}).json()["ip"] == "203.0.113.7"


def test_no_request_leaves_the_shared_session_inside_a_transaction(client, anon):
    """Une lecture ne doit pas garder une connexion ouverte "en transaction" (une base hebergee ne pourrait plus se mettre en veille)."""
    client.get("/user/me")
    anon.get("/health")
    with A.db_lock:
        assert not A.session.in_transaction()
    pid = new_player(client)
    client.get(f"/shop/inventory/{pid}")
    with A.db_lock:
        assert not A.session.in_transaction()


@pytest.mark.parametrize("pasted", [
    'postgresql://u:p@host/db?sslmode=require',
    '  postgresql://u:p@host/db?sslmode=require  \n',                           # espaces / retour a la ligne
    '"postgresql://u:p@host/db?sslmode=require"',                              # guillemets
    "'postgresql://u:p@host/db?sslmode=require'",
    'DATABASE_URL="postgresql://u:p@host/db?sslmode=require"',                 # ligne de fichier .env copiee entiere
    "DATABASE_URL=postgres://u:p@host/db?sslmode=require",
    "psql 'postgresql://u:p@host/db?sslmode=require'",                         # commande psql copiee entiere
])
def test_database_url_survives_typical_copy_paste_mistakes(monkeypatch, pasted):
    import database
    monkeypatch.setenv("GTN_DATABASE_URL", pasted)
    assert database.database_url() == "postgresql+psycopg://u:p@host/db?sslmode=require"


def test_a_value_that_is_not_an_address_gives_a_readable_error_without_leaking_it(monkeypatch):
    import database
    monkeypatch.setenv("GTN_DATABASE_URL", "my-secret-password-123")
    with pytest.raises(RuntimeError) as e:
        database.database_url()
    assert "postgresql://" in str(e.value) and "my-secret-password-123" not in str(e.value)
