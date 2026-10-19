import pytest
from conftest import give, secret, db
import all as A
import engine
from engine.power_up import is_prime, is_perfect


def start_classic(client, player, level=1):
    return client.post("/game/classic/level", json={"level": level, "player_id": player}).json()


def start_discovery(client, player, rng=50):
    return client.post("/game/discovery/start", json={"player_id": player, "max_range": rng}).json()


def use(client, player, sid, item):
    return client.post("/game/powerup", json={"session_id": sid, "player_id": player, "item_id": item})


def guess(client, player, sid, n):
    return client.post("/game/guess", json={"session_id": sid, "player_id": player, "number": n})


def test_number_helpers():
    assert [n for n in range(0, 30) if is_prime(n)] == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert [n for n in range(0, 600) if is_perfect(n)] == [6, 28, 496]


def test_inventory_follows_purchases_and_uses(client, player):
    assert client.get(f"/shop/inventory/{player}").json() == {"items": {}}
    client.post("/shop/buy", json={"playerId": player, "itemId": 3})
    client.post("/shop/buy", json={"playerId": player, "itemId": 3})
    assert client.get(f"/shop/inventory/{player}").json() == {"items": {"3": 2}}
    s = start_classic(client, player)
    assert use(client, player, s["session_id"], 3).json()["remaining"] == 1
    assert client.get(f"/shop/inventory/{player}").json() == {"items": {"3": 1}}
    assert client.get("/shop/inventory/nobody").status_code == 403     # not yours (and no hint whether it exists)


def test_cannot_use_what_you_do_not_own_or_twice(client, player):
    s = start_classic(client, player)
    assert use(client, player, s["session_id"], 1).status_code == 409           # not owned
    give(player, 1, 3)
    assert use(client, player, s["session_id"], 1).status_code == 200
    assert use(client, player, s["session_id"], 1).status_code == 409           # once per game
    assert client.get(f"/shop/inventory/{player}").json()["items"]["1"] == 2    # only one consumed


def test_other_players_session_is_off_limits(client, player):
    other = client.post("/user/new_player").json()["id"]
    give(other, 1)
    s = start_classic(client, player)
    assert use(client, other, s["session_id"], 1).status_code == 403


@pytest.mark.parametrize("item,kind,check", [
    (1, "parity", lambda r, n: r["value"] == ("pair" if n % 2 == 0 else "impair")),
    (5, "prime", lambda r, n: r["value"] == is_prime(n)),
    (6, "perfect", lambda r, n: r["value"] == is_perfect(n)),
])
def test_reveal_items_tell_the_truth(client, player, item, kind, check):
    give(player, item)
    s = start_discovery(client, player, 100)
    r = use(client, player, s["session_id"], item).json()
    assert r["kind"] == kind and check(r, secret(s["session_id"]))


def test_scan_halves_the_range_and_keeps_the_answer_inside(client, player):
    with db() as s:
        s.query(A.Player).filter_by(id=player).first().level = 10      # unlock level 10 (range 1..100)
    for _ in range(25):
        give(player, 2)
        s = start_classic(client, player, level=10)       # 1..100
        r = use(client, player, s["session_id"], 2).json()
        assert r["lo"] <= secret(s["session_id"]) <= r["hi"]
        assert r["hi"] - r["lo"] + 1 == 50


def test_advisor_suggests_the_midpoint_of_what_is_still_possible(client, player):
    give(player, 4)
    s = start_discovery(client, player, 100)
    sid, n = s["session_id"], secret(s["session_id"])
    for g in (0, 100):
        if g != n:
            guess(client, player, sid, g)
    r = use(client, player, sid, 4).json()
    assert r["kind"] == "suggest"
    assert r["lo"] <= n <= r["hi"], "the answer must stay inside the interval"
    assert r["lo"] <= r["number"] <= r["hi"]
    assert r["number"] == (r["lo"] + r["hi"]) // 2
    assert r["hi"] - r["lo"] < 100, "wrong guesses must have narrowed the interval"


def test_life_adds_three_attempts_and_the_level_still_validates(client, player):
    give(player, 3)
    s = start_classic(client, player)
    sid = s["session_id"]
    r = use(client, player, sid, 3).json()
    assert r["attempt_left"] == s["attempt_left"] + 3 and r["max_attempt"] == s["max_attempt"] + 3
    n = secret(sid)
    for wrong in [x for x in range(1, 11) if x != n][: s["max_attempt"] + 2]:     # more than the base allowance
        assert guess(client, player, sid, wrong).status_code == 200
    assert guess(client, player, sid, n).json()["result"] == "OK"
    end = client.post("/game/classic/end_level", json={"session_id": sid, "player_id": player, "status": "win", "level_played": 1, "ended": 0})
    assert end.status_code == 200 and end.json()["coins"] > 0


def test_life_is_not_for_discovery(client, player):
    give(player, 3)
    s = start_discovery(client, player)
    assert use(client, player, s["session_id"], 3).status_code == 422


def test_slow_extends_the_clock_by_at_least_five_seconds(client, player):
    give(player, 7)
    s = start_classic(client, player)
    r = use(client, player, s["session_id"], 7).json()
    assert r["extra"] >= 5
    # the clock is stored server-side too
    with db() as d:
        assert d.query(A.SoloSession).filter_by(id=s["session_id"]).first().time_limit == s["time_limit"] + r["extra"]


def test_multiplier_doubles_coins_and_only_before_the_first_guess(client, player):
    give(player, 8, 2)
    s = start_classic(client, player)
    sid, n = s["session_id"], secret(s["session_id"])
    assert use(client, player, sid, 8).json() == {"item_id": 8, "remaining": 1, "kind": "multiplier", "value": 2}
    assert guess(client, player, sid, n).json()["result"] == "OK"
    end = client.post("/game/classic/end_level", json={"session_id": sid, "player_id": player, "status": "win", "level_played": 1, "ended": 0}).json()
    with db() as d:
        row = d.query(A.GameSession).filter_by(id=sid).first()
        duration = row.ended_time - row.started_time
        inputs = [t.number for t in d.query(A.UserTries).filter_by(session_id=sid).all()]
    base = engine.SoloMode(1).getRewardCoin(inputs, duration, n)
    assert end["coins"] == 2 * base

    s2 = start_classic(client, player)
    guess(client, player, s2["session_id"], 1)
    assert use(client, player, s2["session_id"], 8).status_code == 409       # too late (item kept)
    assert client.get(f"/shop/inventory/{player}").json()["items"]["8"] == 1


def test_finished_games_reject_power_ups(client, player):
    give(player, 1)
    s = start_classic(client, player)
    client.post("/game/classic/end_level", json={"session_id": s["session_id"], "player_id": player, "status": "lose", "level_played": 1, "ended": 0})
    assert use(client, player, s["session_id"], 1).status_code == 409
