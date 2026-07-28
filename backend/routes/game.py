# type: ignore
from fastapi import APIRouter 
from all import *
import engine
from routes.game_mode.endless_mode import router as endless_mode_router
from routes.game_mode.discovery_mode import router as discovery_mode_router
from routes.game_mode.classic_mode import router as classic_mode_router


types = ["solo","discover"]


LEVELS = [{"level" : i , "exp" : 1000*i} for i in range(1 , 1000)]

router = APIRouter(prefix="/game")
router.include_router(endless_mode_router)
router.include_router(discovery_mode_router)
router.include_router(classic_mode_router)

# quand le joueur tente de guess
@router.post("/guess")
def guess(guessdata: GuessData):
    
    that_session = session.query(GameSession).filter_by(id=guessdata.session_id).first()
    if not that_session:
        return
    

    relation = UserTries(
        id = str(uuid4()),
        session_id  = that_session.id,
        number = guessdata.number,
        player_id = that_session.player.id
    )
    session.add(relation )

    
    distance = float(abs(that_session.number-guessdata.number))
    result = engine.checkResult(that_session.number , guessdata.number)

    if that_session.type in (SOLO_MODE,ENDLESS_MODE) :
        print("oui oui oui")
        that_session.attempt_left -= 1


    session.commit()

    print(that_session.number)
    


    return GuessResponse(result=result,
                         attempt_left=that_session.attempt_left, 
                         distance = distance,
                         type = that_session.type)     


