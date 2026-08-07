# type: ignore
from fastapi import APIRouter , HTTPException
from all import *
import engine
from routes.game_mode.endless_mode import router as endless_mode_router
from routes.game_mode.discovery_mode import router as discovery_mode_router
from routes.game_mode.classic_mode import router as classic_mode_router
from routes.game_mode.duel_mode import router as duel_mode_router




LEVELS = [{"level" : i , "exp" : 1000*i} for i in range(1 , 1000)]

router = APIRouter(prefix="/game")
router.include_router(endless_mode_router)
router.include_router(discovery_mode_router)
router.include_router(classic_mode_router)
router.include_router(duel_mode_router)

# quand le joueur tente de guess
@router.post("/guess")
def guess(guessdata: GuessData):

    that_session = session.query(GameSession).filter_by(id=guessdata.session_id).first() 
    if not that_session:
        return HTTPException(status_code=404 , detail="something is missing")


    instance = UserTries(
        id = str(uuid4()),
        session_id = guessdata.session_id,
        number = guessdata.number,
        player_id = guessdata.player_id,
        session_type = that_session.type
    )
    
    distance = float(abs(that_session.number-guessdata.number))
    result = engine.checkResult(that_session.number , guessdata.number)

    if that_session.type in (ENDLESS_MODE , SOLO_MODE) :
        that_session.attempt_left -= 1

    session.add(instance)
    session.commit()




    return GuessResponse(result=result,
                        attempt_left=that_session.attempt_left if that_session.type != engine.DiscoverMode.MODE else -1, 
                        max_attempt = that_session.max_attempt if that_session.type != engine.DiscoverMode.MODE else -1,
                        distance = distance,
                        type = that_session.type
                        )     

