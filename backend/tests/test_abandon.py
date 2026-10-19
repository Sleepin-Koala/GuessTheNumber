"""Joueurs qui partent: abandon, inactivite, salles oubliees, deconnexions."""
import time
import pytest

import all as A
from conftest import secret, db
from routes.game_mode import duel_mode as D
from routes.realtime import hub
from test_duel import host, join, hide, guess, new_player, status, coins
from test_realtime import room_ws, recv_until

pytestmark = pytest.mark.timeout(25)


@pytest.fixture(autouse=True)
def clean_hub():
    hub.grace.clear()
    yield
    hub.grace.clear()


def wait_until(cond, seconds=3.0):
    end = time.time() + seconds
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.02)
    return False


def started(client, bet=100):
    """Une partie en cours: manche 1, l'hote doit cacher son nombre."""
    h, g = new_player(client), new_player(client)
    rid = host(client, h, bet=bet, rng=20)["room_id"]
    join(client, g, rid)
    return h, g, rid


def forfeit(client, rid, pid):
    return client.post(f"/game/duel/rooms/{rid}/forfeit", json={"player_id": pid})


# ----------------------------------------------------------------- abandon volontaire
def test_forfeit_gives_the_win_and_the_bet_to_the_opponent(client):
    h, g, rid = started(client, bet=100)
    hide(client, rid, h, 7)
    r = forfeit(client, rid, g).json()
    assert (r["status"], r["winner_id"], r["end_reason"]) == ("finished", h, "forfeit")
    assert (coins(client, h), coins(client, g)) == (600, 400)


def test_forfeit_is_pushed_to_the_other_player(client):
    h, g, rid = started(client)
    with room_ws(client, rid, h) as wh:
        wh.receive_json()
        forfeit(client, rid, g)
        end = recv_until(wh, "room", lambda m: m["room"]["status"] == "finished")
        assert end["room"]["end_reason"] == "forfeit" and end["room"]["winner_id"] == h


def test_forfeit_rules(client):
    h, g, rid = started(client)
    stranger = new_player(client)
    assert forfeit(client, rid, stranger).status_code == 403
    assert forfeit(client, rid, g).status_code == 200
    assert forfeit(client, rid, h).status_code == 409                    # already over
    waiting = host(client, h)["room_id"]
    assert forfeit(client, waiting, h).status_code == 409                # nothing to forfeit yet: use leave instead


def test_a_loser_who_cannot_pay_only_loses_what_they_have(client):
    h, g, rid = started(client, bet=300)
    with db() as s:
        s.query(A.Player).filter_by(id=g).first().coins = 120
    forfeit(client, rid, g)
    assert (coins(client, h), coins(client, g)) == (620, 0)


# ----------------------------------------------------------------- inactivite
def test_idle_hider_loses_by_timeout_but_not_before(client):
    h, g, rid = started(client)
    room = status(client, rid)
    assert room["turn_deadline"] == pytest.approx(time.time() + D.TURN_TIMEOUT, abs=5)
    D.sweep(now=time.time() + D.TURN_TIMEOUT - 5)
    assert status(client, rid)["status"] == "round1_hide"                # not yet
    D.sweep(now=time.time() + D.TURN_TIMEOUT + 5)
    end = status(client, rid)
    assert (end["status"], end["winner_id"], end["end_reason"]) == ("finished", g, "timeout")   # the host never hid a number
    assert coins(client, g) == 600 and coins(client, h) == 400


def test_idle_guesser_loses_by_timeout(client):
    h, g, rid = started(client)
    hide(client, rid, h, 7)
    D.sweep(now=time.time() + D.TURN_TIMEOUT + 5)
    end = status(client, rid)
    assert (end["winner_id"], end["end_reason"]) == (h, "timeout")        # the guest never guessed


def test_every_move_restarts_the_clock(client):
    h, g, rid = started(client)
    hide(client, rid, h, 7)
    before = status(client, rid)["turn_deadline"]
    time.sleep(0.05)
    guess(client, rid, g, 1)
    assert status(client, rid)["turn_deadline"] > before


def test_forgotten_waiting_rooms_expire_and_leave_the_lobby(client):
    h = new_player(client)
    rid = host(client, h)["room_id"]
    with client.websocket_connect("/game/duel/ws-lobby") as lobby:
        lobby.receive_json()
        D.sweep(now=time.time() + D.WAIT_TIMEOUT + 5)
        msg = recv_until(lobby, "lobby", lambda m: all(r["room_id"] != rid for r in m["rooms"]))
        assert all(r["room_id"] != rid for r in msg["rooms"])
    room = status(client, rid)
    assert (room["status"], room["end_reason"]) == ("cancelled", "expired")


def test_finished_rooms_have_no_deadline(client):
    h, g, rid = started(client)
    forfeit(client, rid, h)
    room = status(client, rid)
    assert room["turn_deadline"] is None and room["server_time"] == pytest.approx(time.time(), abs=5)


# ----------------------------------------------------------------- deconnexions
def test_disconnect_warns_the_opponent_and_a_quick_return_cancels_it(client):
    h, g, rid = started(client)
    with room_ws(client, rid, h) as wh:
        with room_ws(client, rid, g):
            recv_until(wh, "presence", lambda m: set(m["online"]) == {h, g})
        grace = recv_until(wh, "grace")                                    # the guest's socket closed
        assert grace["player_id"] == g
        assert grace["deadline"] == pytest.approx(time.time() + D.DISCONNECT_GRACE, abs=5)
        with room_ws(client, rid, g):                                      # ...and comes back in time
            assert recv_until(wh, "grace_cleared")["player_id"] == g
            D.sweep(now=grace["deadline"] + 1)                             # nothing happens: they are back
            assert status(client, rid)["status"] == "round1_hide"


def test_disconnect_that_lasts_forfeits_the_game(client):
    h, g, rid = started(client, bet=100)
    with room_ws(client, rid, h) as wh:
        with room_ws(client, rid, g):
            recv_until(wh, "presence", lambda m: set(m["online"]) == {h, g})
        grace = recv_until(wh, "grace")
        D.sweep(now=grace["deadline"] + 1)
        end = recv_until(wh, "room", lambda m: m["room"]["status"] == "finished")["room"]
        assert (end["winner_id"], end["end_reason"]) == (h, "disconnect")
    assert (coins(client, h), coins(client, g)) == (600, 400)


def test_nobody_wins_when_both_players_are_gone(client):
    h, g, rid = started(client, bet=100)
    with room_ws(client, rid, h) as wh:
        with room_ws(client, rid, g):
            recv_until(wh, "presence", lambda m: set(m["online"]) == {h, g})
        recv_until(wh, "grace")
    assert wait_until(lambda: not hub.is_online(rid, h) and hub.graces_for(rid) and len(hub.graces_for(rid)) == 2)
    D.sweep(now=time.time() + D.DISCONNECT_GRACE + 5)
    end = status(client, rid)
    assert (end["status"], end["end_reason"], end["winner_id"]) == ("cancelled", "abandoned", None)
    assert (coins(client, h), coins(client, g)) == (500, 500)              # no coins moved


def test_a_host_who_leaves_an_empty_room_cancels_it(client):
    h = new_player(client)
    rid = host(client, h)["room_id"]
    with room_ws(client, rid, h) as wh:
        wh.receive_json()
    assert wait_until(lambda: hub.graces_for(rid))
    D.sweep(now=time.time() + D.DISCONNECT_GRACE + 5)
    assert status(client, rid)["end_reason"] == "abandoned"


def test_someone_arriving_late_is_told_who_is_already_disconnecting(client):
    h, g, rid = started(client)
    with room_ws(client, rid, h) as wh:
        wh.receive_json()
    assert wait_until(lambda: hub.graces_for(rid))
    with room_ws(client, rid, g) as wg:
        assert recv_until(wg, "grace")["player_id"] == h


def test_a_player_back_after_the_deadline_finds_the_finished_game(client):
    h, g, rid = started(client)
    with room_ws(client, rid, g):
        pass
    assert wait_until(lambda: hub.graces_for(rid))
    with room_ws(client, rid, h) as wh:
        D.sweep(now=time.time() + D.DISCONNECT_GRACE + 5)
        recv_until(wh, "room", lambda m: m["room"]["status"] == "finished")
    with room_ws(client, rid, g) as wg:
        snap = wg.receive_json()["room"]
        assert (snap["status"], snap["end_reason"], snap["winner_id"]) == ("finished", "disconnect", h)
