import json
import pytest
from starlette.websockets import WebSocketDisconnect

from test_duel import host, join, hide, guess, new_player, status

pytestmark = pytest.mark.timeout(20)     # une socket qui ne recoit rien ferait sinon bloquer le test


def room_ws(client, room_id, player_id):
    return client.websocket_connect(f"/game/duel/ws/{room_id}?player_id={player_id}")


def recv_until(ws, kind, predicate=lambda m: True, limit=12):
    """Lit les messages jusqu'a en trouver un du bon type (les `presence` s'intercalent)."""
    seen = []
    for _ in range(limit):
        msg = ws.receive_json()
        seen.append(msg)
        if msg["type"] == kind and predicate(msg):
            return msg
    raise AssertionError(f"no {kind} message in {seen}")


def test_member_gets_a_snapshot_and_strangers_are_refused(client):
    h, stranger = new_player(client), new_player(client)
    rid = host(client, h)["room_id"]
    with room_ws(client, rid, h) as ws:
        snap = ws.receive_json()
        assert snap["type"] == "room" and snap["room"]["room_id"] == rid and snap["room"]["status"] == "waiting"
    with pytest.raises(WebSocketDisconnect) as e:
        with room_ws(client, rid, stranger):
            pass
    assert e.value.code == 4403
    with pytest.raises(WebSocketDisconnect) as e:
        with room_ws(client, "nope", h):
            pass
    assert e.value.code == 4404


def test_every_action_is_pushed_to_both_players(client):
    h, g = new_player(client), new_player(client)
    rid = host(client, h, bet=10, rng=20)["room_id"]
    with room_ws(client, rid, h) as wh:
        assert wh.receive_json()["room"]["status"] == "waiting"
        join(client, g, rid)
        with room_ws(client, rid, g) as wg:
            joined = recv_until(wh, "room", lambda m: m["room"]["status"] == "round1_hide")
            assert joined["room"]["guest_name"]
            assert recv_until(wg, "room")["room"]["status"] == "round1_hide"       # snapshot on connect

            hide(client, rid, h, 7)
            assert recv_until(wg, "room", lambda m: m["room"]["status"] == "round1_guess")
            assert recv_until(wh, "room", lambda m: m["room"]["status"] == "round1_guess")

            guess(client, rid, g, 3)
            for ws in (wg, wh):
                m = recv_until(ws, "room", lambda m: m["room"]["last_feedback"] == "MOINS")
                assert m["room"]["round1_attempts_used"] == 1

            guess(client, rid, g, 7)
            assert recv_until(wh, "room", lambda m: m["room"]["status"] == "round2_hide")
            hide(client, rid, g, 4)
            guess(client, rid, h, 4)
            end = recv_until(wg, "room", lambda m: m["room"]["status"] == "finished")
            assert end["room"]["winner_id"] == h


def test_pushed_messages_never_contain_secret_numbers(client):
    h, g = new_player(client), new_player(client)
    rid = host(client, h, rng=20)["room_id"]
    join(client, g, rid)
    with room_ws(client, rid, g) as wg:
        hide(client, rid, h, 13)
        guess(client, rid, g, 1)
        text = []
        for _ in range(4):
            text.append(json.dumps(recv_until(wg, "room", limit=6)))
            if "last_feedback" in text[-1] and '"MOINS"' in text[-1]:
                break
    blob = " ".join(text)
    assert "hider_number" not in blob and "guesser_number" not in blob


def test_presence_tracks_who_is_connected(client):
    h, g = new_player(client), new_player(client)
    rid = host(client, h)["room_id"]
    join(client, g, rid)
    with room_ws(client, rid, h) as wh:
        assert recv_until(wh, "presence", lambda m: m["online"] == [h])
        with room_ws(client, rid, g):
            assert recv_until(wh, "presence", lambda m: set(m["online"]) == {h, g})
        assert recv_until(wh, "presence", lambda m: m["online"] == [h])         # the guest left


def test_lobby_socket_follows_rooms_opening_and_closing(client):
    h, g = new_player(client), new_player(client)
    with client.websocket_connect("/game/duel/ws-lobby") as lobby:
        assert lobby.receive_json()["type"] == "lobby"
        rid = host(client, h, name="Live room")["room_id"]
        assert any(r["room_id"] == rid for r in recv_until(lobby, "lobby", lambda m: any(r["room_id"] == rid for r in m["rooms"]))["rooms"])
        join(client, g, rid)
        gone = recv_until(lobby, "lobby", lambda m: all(r["room_id"] != rid for r in m["rooms"]))
        assert all(r["room_id"] != rid for r in gone["rooms"])


def test_cancelling_a_room_is_pushed(client):
    h = new_player(client)
    rid = host(client, h)["room_id"]
    with room_ws(client, rid, h) as wh:
        wh.receive_json()
        client.post(f"/game/duel/rooms/{rid}/leave", json={"player_id": h})
        assert recv_until(wh, "room", lambda m: m["room"]["status"] == "cancelled")


def test_ping_gets_a_pong(client):
    h = new_player(client)
    rid = host(client, h)["room_id"]
    with room_ws(client, rid, h) as ws:
        ws.receive_json()
        ws.send_json({"type": "ping"})
        assert recv_until(ws, "pong")


def test_http_keeps_working_while_sockets_are_open(client):
    """Une socket ne doit jamais tenir le verrou de la base (sinon tout le serveur se figerait)."""
    h = new_player(client)
    rid = host(client, h)["room_id"]
    with room_ws(client, rid, h) as ws, client.websocket_connect("/game/duel/ws-lobby") as lobby:
        ws.receive_json(); lobby.receive_json()
        assert client.get("/health").status_code == 200
        assert client.get(f"/user/{h}").status_code == 200
        assert status(client, rid)["status"] == "waiting"
