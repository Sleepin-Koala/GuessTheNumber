# type: ignore

from fastapi import APIRouter , HTTPException
from all import *
import engine




router = APIRouter(prefix="/endless")

@router.post("/start")
def start_endless(EndlessData: EndlessData):
    
    player = session.query(Player).filter_by(id = EndlessData.player_id).first()
    _ThatSession = session.query(GameSession).filter_by(type = "endless" , player_id = EndlessData.player_id , status = "continued").all()
    if not player :
        raise HTTPException(300)

    
    print(EndlessData.new_session)

    if EndlessData.new_session:
        currentStage = 1
        print('ahi mais cest ça ')
        for s in _ThatSession:
            s.status = "ended"

        new_session = GameSession(
                id = str(uuid4()),
                max_attempt = 5,
                attempt_left= 5,
                number=engine.EndlessMode.newSession(1),
                status="continued",
                started_time = time.time(),
                end_time = 0,       
                player_id = EndlessData.player_id,
                type = "endless",
                time_limit = -1,
                result = GIVEN_UP,
                stage = 1
            )
    else :
        currentStage = len(_ThatSession)+1
        new_session = GameSession(
            id = str(uuid4()),
            max_attempt = 5,
            attempt_left= 5,
            number=engine.EndlessMode.newSession(currentStage),
            status="continued",
            started_time = time.time(),
            end_time = 0,       
            player_id = EndlessData.player_id,
            type = "endless",
            time_limit = -1,
            result = GIVEN_UP,
            stage = currentStage
        )
        print(currentStage)

    session.add(new_session)
    session.commit()
    
    
    return EndlessModeResponse(
        session_id= new_session.id,  
        max_attempt=new_session.max_attempt, 
        attempt_left=new_session.attempt_left, 
        max_range = currentStage*10,
        time_limit = new_session.time_limit,
        bet = EndlessData.bet,
        winnable=0,
        stage = currentStage
    )





@router.post("/end_session")
def SessionFinished(EndlessEndSessionData :EndlessEndSessionData):
    
    that_session = session.query(GameSession).filter_by(id = EndlessEndSessionData.session_id).first()
    user = session.query(Player).filter_by(id = EndlessEndSessionData.player_id).first()  
    if not user or not that_session or not session:
        return
    
    if EndlessEndSessionData.status == engine.EndlessMode.WIN: 
        that_session.result = engine.EndlessMode.STAGEPASSED


    that_session.end_time = EndlessEndSessionData.ended
    
    session.commit()

    return PlayerData(id = user.id , name = user.name , gems = user.gems , coins = user.coins , xp = user.xp , level = user.level)

