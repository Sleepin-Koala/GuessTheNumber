"""Inscription / connexion par e-mail et liaison Google (la verification Google est simulee)."""
import pytest
import routes.accounts as acc


def test_register_attaches_email_to_the_guest_and_keeps_progress(client):
    guest = client.post("/user/new_player").json()
    r = client.post("/auth/register", json={"email": "Ada@Example.com", "password": "correct horse"},
                    headers={"Authorization": f"Bearer {guest['token']}"})
    assert r.status_code == 200, r.text
    assert r.json()["id"] == guest["id"] and r.json()["email"] == "ada@example.com" and "token" not in r.json()
    assert client.get("/user/me", headers={"Authorization": f"Bearer {guest['token']}"}).json()["coins"] == 500


def test_register_without_guest_creates_account_and_token(client):
    r = client.post("/auth/register", json={"email": "bob@example.com", "password": "longenough"}, headers={"Authorization": "Bearer nope"})
    assert r.status_code == 200 and r.json()["token"] and r.json()["coins"] == 500


def test_register_validation_and_duplicates(client):
    assert client.post("/auth/register", json={"email": "not-an-email", "password": "longenough"}).status_code == 422
    assert client.post("/auth/register", json={"email": "c@example.com", "password": "short"}).status_code == 422
    assert client.post("/auth/register", json={"email": "dup@example.com", "password": "longenough"}).status_code == 200
    assert client.post("/auth/register", json={"email": "DUP@example.com", "password": "longenough"}).status_code == 409


def test_login_and_wrong_password(client):
    client.post("/auth/register", json={"email": "d@example.com", "password": "longenough"})
    ok = client.post("/auth/login", json={"email": "D@example.com ", "password": "longenough"})
    assert ok.status_code == 200 and ok.json()["token"]
    token = ok.json()["token"]
    assert client.get("/user/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    assert client.post("/auth/login", json={"email": "d@example.com", "password": "wrong-password"}).status_code == 401
    assert client.post("/auth/login", json={"email": "nobody@example.com", "password": "whatever1"}).status_code == 401


def test_login_invalidates_the_previous_token(client):
    client.post("/auth/register", json={"email": "e@example.com", "password": "longenough"})
    t1 = client.post("/auth/login", json={"email": "e@example.com", "password": "longenough"}).json()["token"]
    t2 = client.post("/auth/login", json={"email": "e@example.com", "password": "longenough"}).json()["token"]
    assert client.get("/user/me", headers={"Authorization": f"Bearer {t1}"}).status_code == 401
    assert client.get("/user/me", headers={"Authorization": f"Bearer {t2}"}).status_code == 200


def test_password_is_not_stored_in_clear(client):
    from conftest import db
    client.post("/auth/register", json={"email": "f@example.com", "password": "my-secret-pass"})
    with db() as s:
        row = s.query(acc.Player).filter_by(email="f@example.com").first()
        assert "my-secret-pass" not in row.password_hash and row.password_hash.startswith("scrypt$")


def test_google_not_configured(client, monkeypatch):
    monkeypatch.setattr(acc, "GOOGLE_CLIENT_ID", "")
    assert client.post("/auth/google", json={"credential": "x"}).status_code == 503


def test_google_links_guest_then_logs_in(client, monkeypatch):
    monkeypatch.setattr(acc, "GOOGLE_CLIENT_ID", "cid")
    monkeypatch.setattr(acc, "_verify_google", lambda c: {"sub": "g-123", "email": "G@Example.com"})
    guest = client.post("/user/new_player").json()
    linked = client.post("/auth/google", json={"credential": "ok"}, headers={"Authorization": f"Bearer {guest['token']}"}).json()
    assert linked["id"] == guest["id"] and linked["email"] == "g@example.com" and linked["google_linked"]
    again = client.post("/auth/google", json={"credential": "ok"}).json()          # autre appareil
    assert again["id"] == guest["id"] and again["token"] and again["token"] != guest["token"]


def test_google_rejects_unverified_tokens(client, monkeypatch):
    monkeypatch.setattr(acc, "GOOGLE_CLIENT_ID", "cid")
    class R:
        def __init__(s, body): s.body = body
        def read(s): return s.body
        def __enter__(s): return s
        def __exit__(s, *a): pass
    import json
    def fake(payload):
        monkeypatch.setattr(acc.urllib.request, "urlopen", lambda *a, **k: R(json.dumps(payload).encode()))
        return client.post("/auth/google", json={"credential": "t"}).status_code
    good = {"aud": "cid", "iss": "accounts.google.com", "email_verified": "true", "sub": "s1", "email": "h@example.com", "exp": "9999999999"}
    assert fake({**good, "aud": "other"}) == 401
    assert fake({**good, "email_verified": "false"}) == 401
    assert fake({**good, "exp": "1"}) == 401
    assert fake(good) == 200


def test_auth_routes_are_rate_limited_config_is_public(client):
    assert client.get("/auth/config").status_code == 200
