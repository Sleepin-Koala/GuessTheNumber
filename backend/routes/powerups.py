# type: ignore
import math
import random
from fastapi import APIRouter , HTTPException
from all import *
from engine.power_up import pair_impair , is_prime , is_perfect
from routes.utils import get_owned_session , ensure_open

router = APIRouter()

ITEM_PARITY, ITEM_SCAN, ITEM_LIFE, ITEM_ADVISOR, ITEM_PRIME, ITEM_PERFECT, ITEM_SLOW, ITEM_MULTIPLIER = range(1, 9)

LIFE_BONUS = 3          # essais ajoutes par "Vie bonus"
MIN_SLOW_EXTRA = 5      # secondes ajoutees au minimum par "Ralenti"

# quels power-ups ont un sens dans quel mode
ALLOWED = {
    "solo":     {ITEM_PARITY, ITEM_SCAN, ITEM_LIFE, ITEM_ADVISOR, ITEM_PRIME, ITEM_PERFECT, ITEM_SLOW, ITEM_MULTIPLIER},
    "discover": {ITEM_PARITY, ITEM_SCAN, ITEM_ADVISOR, ITEM_PRIME, ITEM_PERFECT},
    "endless":  {ITEM_PARITY, ITEM_SCAN, ITEM_LIFE, ITEM_ADVISOR, ITEM_PRIME, ITEM_PERFECT},
}


def _bounds(that_session):
    """Intervalle encore possible d'apres les propositions deja faites."""
    floor = 0 if that_session.type == "discover" else 1
    lo, hi = floor, that_session.max_range or max(that_session.number * 2, 10)
    for t in session.query(UserTries).filter_by(session_id = that_session.id).all():
        if t.number < that_session.number:
            lo = max(lo , t.number + 1)
        elif t.number > that_session.number:
            hi = min(hi , t.number - 1)
    return lo , hi


@router.post("/powerup")
def use_powerup(data: PowerupData):
    that = get_owned_session(data.session_id , data.player_id)
    ensure_open(that)

    if data.item_id not in ALLOWED.get(that.type , set()):
        raise HTTPException(status_code=422 , detail="This power-up cannot be used in this mode")
    if session.query(SessionPowerup).filter_by(session_id = that.id , item_id = data.item_id).count():
        raise HTTPException(status_code=409 , detail="Already used in this game")
    holding = session.query(PlayerItems).filter_by(playerId = data.player_id , itemId = data.item_id).first()
    if holding is None or (holding.amount or 0) < 1:
        raise HTTPException(status_code=409 , detail="Not in your inventory")

    n = that.number
    if data.item_id == ITEM_MULTIPLIER and session.query(UserTries).filter_by(session_id = that.id).count():
        raise HTTPException(status_code=409 , detail="Must be used before the first guess")

    if data.item_id == ITEM_PARITY:
        result = {"kind": "parity" , "value": pair_impair(n)}
    elif data.item_id == ITEM_PRIME:
        result = {"kind": "prime" , "value": is_prime(n)}
    elif data.item_id == ITEM_PERFECT:
        result = {"kind": "perfect" , "value": is_perfect(n)}
    elif data.item_id == ITEM_SCAN:
        max_range = that.max_range or max(n * 2 , 10)
        width = max(1 , math.ceil(max_range / 2))
        lo_min = max(1 , n - width + 1)
        lo_max = max(lo_min , min(n , max_range - width + 1))
        lo = random.randint(lo_min , lo_max)
        result = {"kind": "range" , "lo": lo , "hi": min(max_range , lo + width - 1)}
    elif data.item_id == ITEM_ADVISOR:
        lo , hi = _bounds(that)
        result = {"kind": "suggest" , "number": (lo + hi) // 2 , "lo": lo , "hi": hi}
    elif data.item_id == ITEM_LIFE:
        that.attempt_left += LIFE_BONUS
        that.max_attempt += LIFE_BONUS
        result = {"kind": "attempts" , "extra": LIFE_BONUS , "attempt_left": that.attempt_left , "max_attempt": that.max_attempt}
    elif data.item_id == ITEM_SLOW:
        remaining = max(0.0 , that.time_limit - (time.time() - that.started_time))
        extra = max(MIN_SLOW_EXTRA , round(remaining))
        that.time_limit += extra
        result = {"kind": "time" , "extra": extra}
    else:  # ITEM_MULTIPLIER
        result = {"kind": "multiplier" , "value": 2}

    holding.amount -= 1
    session.add(SessionPowerup(id = str(uuid4()) , session_id = that.id , player_id = data.player_id , item_id = data.item_id , created_at = time.time()))
    session.commit()

    return {"item_id": data.item_id , "remaining": holding.amount , **result}
