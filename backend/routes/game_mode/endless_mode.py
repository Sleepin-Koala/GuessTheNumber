# type: ignore

from fastapi import APIRouter , HTTPException
from all import *
import engine
from routes.utils import get_player_or_404 , get_owned_session , ensure_open




router = APIRouter(prefix="/endless")

MAX_STAGE = 100

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
        max_attempt = 5,
        attempt_left= 5,
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
        user.coins += reward
    elif EndlessEndSessionData.status == str(engine.EndlessMode.LOSE):
        that_session.status = engine.EndlessMode.LOSE
    else:
        raise HTTPException(status_code=422 , detail="status must be 'win' or 'lose'")

    that_session.ended_time = time.time()
    
    session.commit()

    return reward
