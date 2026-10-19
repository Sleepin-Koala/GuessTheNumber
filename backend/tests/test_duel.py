import all as A
from conftest import secret


def coins(client, pid):
    return client.get(f"/user/{pid}").json()["coins"]


def new_player(client):
    return client.post("/user/new_player").json()["id"]


def host(client, pid, bet=100, rng=20, name="Salle"):
    return client.post("/game/duel/host", json={"host_id": pid, "name": name, "amount": bet, "max_range": rng}).json()


def join(client, pid, rid):
    return client.post("/game/duel/join", json={"player_id": pid, "room_id": rid})


def hide(client, rid, pid, n):
    return client.post(f"/game/duel/rooms/{rid}/hide", json={"player_id": pid, "number": n})


def guess(client, rid, pid, n):
    return client.post(f"/game/duel/rooms/{rid}/guess", json={"player_id": pid, "number": n})


def status(client, rid):
    return client.post("/game/duel/status", json={"room_id": rid}).json()


def play(client, h, g, rid, host_hides, guest_hides, host_guesses, guest_guesses):
    """Deroule une partie complete. Round 1: l'hote cache, l'invite devine. Round 2: l'inverse."""
    assert hide(client, rid, h, host_hides).status_code == 200
    for n in guest_guesses:
        r = guess(client, rid, g, n)
        assert r.status_code == 200
    assert hide(client, rid, g, guest_hides).status_code == 200
    for n in host_guesses:
        r = guess(client, rid, h, n)
        assert r.status_code == 200
    return status(client, rid)


def test_room_carries_player_names_and_listing(client):
    h, g = new_player(client), new_player(client)
    room = host(client, h, name="  Duel du soir  ")
    assert room["room_name"] == "Duel du soir" and room["host_name"] and room["guest_name"] is None
    assert room["room_id"] in [r["room_id"] for r in client.get("/game/duel/rooms").json()]
    joined = join(client, g, room["room_id"]).json()
    assert joined["guest_name"] and joined["status"] == "round1_hide"
    assert room["room_id"] not in [r["room_id"] for r in client.get("/game/duel/rooms").json()]


def test_hosting_again_cancels_the_previous_waiting_room(client):
    h = new_player(client)
    first = host(client, h)["room_id"]
    second = host(client, h)["room_id"]
    ids = [r["room_id"] for r in client.get("/game/duel/rooms").json()]
    assert second in ids and first not in ids
    assert status(client, first)["status"] == "cancelled"


def test_host_can_cancel_a_waiting_room_but_not_a_started_game(client):
    h, g = new_player(client), new_player(client)
    rid = host(client, h)["room_id"]
    assert client.post(f"/game/duel/rooms/{rid}/leave", json={"player_id": g}).status_code == 403   # stranger
    assert client.post(f"/game/duel/rooms/{rid}/leave", json={"player_id": h}).json()["status"] == "cancelled"
    assert join(client, g, rid).status_code == 409                                                    # cancelled rooms are closed
    rid2 = host(client, h)["room_id"]
    join(client, g, rid2)
    assert client.post(f"/game/duel/rooms/{rid2}/leave", json={"player_id": h}).status_code == 409


def test_secret_numbers_never_appear_in_room_data(client):
    h, g = new_player(client), new_player(client)
    rid = host(client, h)["room_id"]
    join(client, g, rid)
    hide(client, rid, h, 7)
    assert "7" not in {str(v) for k, v in status(client, rid).items() if k not in ("max_range", "bet_amount")}
    assert "hider_number" not in status(client, rid) and "guesser_number" not in status(client, rid)


def test_fewer_attempts_wins_and_bet_moves_from_loser_to_winner(client):
    h, g = new_player(client), new_player(client)
    rid = host(client, h, bet=100, rng=20)["room_id"]
    join(client, g, rid)
    # guest needs 3 tries for the host's 12, host needs 1 try for the guest's 5 -> host wins
    end = play(client, h, g, rid, host_hides=12, guest_hides=5, host_guesses=[5], guest_guesses=[1, 2, 12])
    assert end["status"] == "finished" and end["winner_id"] == h
    assert (end["round1_attempts_used"], end["round2_attempts_used"]) == (3, 1)
    assert coins(client, h) == 600 and coins(client, g) == 400


def test_guest_wins_when_faster(client):
    h, g = new_player(client), new_player(client)
    rid = host(client, h, bet=50, rng=20)["room_id"]
    join(client, g, rid)
    end = play(client, h, g, rid, host_hides=9, guest_hides=4, host_guesses=[1, 2, 4], guest_guesses=[9])
    assert end["winner_id"] == g and coins(client, g) == 550 and coins(client, h) == 450


def test_tie_goes_to_the_host(client):
    h, g = new_player(client), new_player(client)
    rid = host(client, h, bet=10, rng=20)["room_id"]
    join(client, g, rid)
    end = play(client, h, g, rid, host_hides=3, guest_hides=4, host_guesses=[4], guest_guesses=[3])
    assert end["winner_id"] == h


def test_feedback_and_turn_rules(client):
    h, g = new_player(client), new_player(client)
    rid = host(client, h, rng=20)["room_id"]
    join(client, g, rid)
    assert guess(client, rid, g, 5).status_code == 409                    # nothing hidden yet
    assert hide(client, rid, g, 5).status_code == 403                     # guest is not the hider in round 1
    assert hide(client, rid, h, 99).status_code == 422                    # outside the range
    hide(client, rid, h, 10)
    assert guess(client, rid, h, 5).status_code == 403                    # the hider cannot guess
    r = guess(client, rid, g, 3).json()
    assert (r["last_feedback"], r["last_distance"]) == ("MOINS", 7.0)     # 3 is too small
    assert guess(client, rid, g, 15).json()["last_feedback"] == "PLUS"    # 15 is too big
