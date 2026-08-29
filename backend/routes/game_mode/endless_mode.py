# type: ignore

from fastapi import APIRouter , HTTPException
from all import *
import engine




router = APIRouter(prefix="/endless")

@router.post("/start")
def start_endless(EndlessData: EndlessData):
    player = session.query(Player).filter_by(id = EndlessData.player_id).first()
    if not player :
        raise HTTPException(status_code=404 , detail="Player not found")

    player.coins -= EndlessData.bet


    endless_session = EndlessSession(
        id = str(uuid4()),
        max_attempt = 5,
        attempt_left= 5,
        bet = EndlessData.bet,
        stage = EndlessData.stage,
        number=engine.EndlessMode.newSession(EndlessData.stage),
        status="abandonned",
        started_time = time.time(),
        ended_time = None,  
        player_id = EndlessData.player_id,
        type = "endless"
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
    
    that_session = session.query(GameSession).filter_by(id = EndlessEndSessionData.session_id).first()
    user = session.query(Player).filter_by(id = EndlessEndSessionData.player_id).first()  
    if not user or not that_session or not session or not isinstance(that_session , EndlessSession):
        return HTTPException(status_code=404 , detail="Something is missing")

    if EndlessEndSessionData.status == str(engine.EndlessMode.WIN): 
        that_session.status = engine.EndlessMode.STAGEPASSED


    f = engine.EndlessMode.getRoundReward(int(that_session.stage) , that_session.bet)
    
    user.coins += f


    that_session.ended_time = EndlessEndSessionData.ended
    
    session.commit()

    return f

