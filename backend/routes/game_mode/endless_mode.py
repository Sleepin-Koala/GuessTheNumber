# type: ignore

import math
from fastapi import APIRouter , HTTPException
from all import *
import engine
from routes.utils import get_player_or_404 , get_owned_session , ensure_open , OPEN_STATES




router = APIRouter(prefix="/endless")

MAX_STAGE = 100
HOUSE_EDGE = 0.95   # esperance de gain maximale d'un joueur optimal (recherche dichotomique) = 95 % de la mise


def attempts_for(stage: int) -> int:
    # une recherche dichotomique parfaite doit pouvoir echouer: un essai de moins que le minimum garanti
    return max(1 , math.ceil(math.log2(stage * 10 + 1)) - 1)


def win_probability(stage: int) -> float:
    return min(1.0 , (2 ** attempts_for(stage) - 1) / (stage * 10))

RESUME_WINDOW = 24 * 3600


@router.get("/active")
def active_endless(player_id: str):
    """Palier en cours de ce joueur (rechargement de page, onglet ferme...), pour reprendre ou il s'etait arrete."""
    user = get_player_or_404(player_id)
    that = (session.query(EndlessSession)
            .filter(EndlessSession.player_id == user.id , EndlessSession.status.in_(OPEN_STATES) , EndlessSession.started_time > time.time() - RESUME_WINDOW)
            .order_by(EndlessSession.started_time.desc()).first())
    if not that:
        return None
    tries = [t.number for t in session.query(UserTries).filter_by(session_id = that.id).all()]
    solved = that.number in tries
    if that.attempt_left <= 0 and not solved:
        that.status = engine.EndlessMode.LOSE
        that.ended_time = time.time()
        session.commit()
        return None
    return {
        "session_id": that.id , "max_attempt": that.max_attempt , "attempt_left": that.attempt_left ,
        "max_range": that.max_range , "bet": that.bet , "stage": that.stage , "coins": user.coins ,
        "solved": solved ,
        "tries": [[n , engine.checkResult(that.number , n)] for n in tries] ,
    }


@router.post("/start")
def start_endless(EndlessData: EndlessData):
    player = get_player_or_404(EndlessData.player_id)

    if not 1 <= EndlessData.stage <= MAX_STAGE:
        raise HTTPException(status_code=422 , detail=f"stage must be between 1 and {MAX_STAGE}")
    if EndlessData.bet < 1:
        raise HTTPException(status_code=422 , detail="bet must be positive")
    if EndlessData.bet > player.coins:
        raise HTTPException(status_code=402 , detail="Not enough coins")

    player.coins -= EndlessData.bet


    endless_session = EndlessSession(
        id = str(uuid4()),
        max_attempt = attempts_for(EndlessData.stage),
        attempt_left= attempts_for(EndlessData.stage),
        bet = EndlessData.bet,
        stage = EndlessData.stage,
        number=engine.EndlessMode.newSession(EndlessData.stage),
        status=GIVEN_UP,
        started_time = time.time(),
        ended_time = None,  
        player_id = EndlessData.player_id,
        type = "endless",
        max_range = EndlessData.stage*10,
    )   

    session.add(endless_session)
    session.commit()

    
    
    return EndlessModeResponse(
        session_id= endless_session.id,  
        max_attempt=endless_session.max_attempt, 
        attempt_left=endless_session.attempt_left, 
        max_range = EndlessData.stage*10,
        bet = EndlessData.bet,
        stage = EndlessData.stage,
        coins = player.coins
    )


@router.post("/end_session")
def SessionFinished(EndlessEndSessionData :EndlessEndSessionData):
    
    user = get_player_or_404(EndlessEndSessionData.player_id)
    that_session = get_owned_session(EndlessEndSessionData.session_id , user.id)
    if not isinstance(that_session , EndlessSession):
        raise HTTPException(status_code=404 , detail="Session not found")
    ensure_open(that_session)

    reward = 0
    if EndlessEndSessionData.status == str(engine.EndlessMode.WIN): 
        tries = session.query(UserTries).filter_by(session_id = that_session.id).all()
        if not any(t.number == that_session.number for t in tries):
            raise HTTPException(status_code=409 , detail="The number has not been found")
        that_session.status = engine.EndlessMode.STAGEPASSED
        reward = engine.EndlessMode.getRoundReward(int(that_session.stage) , that_session.bet)
        reward = min(reward , int(that_session.bet * HOUSE_EDGE / win_probability(int(that_session.stage))))
        user.coins += reward
    elif EndlessEndSessionData.status == str(engine.EndlessMode.LOSE):
        that_session.status = engine.EndlessMode.LOSE
    else:
        raise HTTPException(status_code=422 , detail="status must be 'win' or 'lose'")

    that_session.ended_time = time.time()
    
    session.commit()

    return reward
