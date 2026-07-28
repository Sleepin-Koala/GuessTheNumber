 # type: ignore
import engine
from all import *
from fastapi import APIRouter , HTTPException

router = APIRouter(prefix="/discovery")


@router.post("/start")
def start_discovery(DiscoverData: DiscoverData):
    player = session.query(Player).filter(Player.id == DiscoverData.player_id).first()
    if not player:
        return 
    
    new_session = GameSession(
        id=str(uuid4()),
        max_attempt=-1,
        attempt_left=-1,
        number=engine.DiscoverMode.get_random(DiscoverData.max_range),
        status="continued",
        started_time = time.time(),
        end_time = 0,
        player_id = DiscoverData.player_id,
        type = "discover",
        time_limit = -1,
        result = GIVEN_UP
    )
    
    session.add(new_session)
    session.commit()
    
    
    return DiscoverModeResponse(
        session_id = new_session.id,   
        max_range = DiscoverData.max_range,
    )


@router.post("/end_session")
def SessionFinished(DiscoveryEndSessionData :DiscoveryEndSessionData):
    
    that_session = session.query(GameSession).filter_by(id = DiscoveryEndSessionData.session_id).first()
    user = session.query(Player).filter_by(id = DiscoveryEndSessionData.player_id).first()  
    if not user or not that_session or not session:
        return

    that_session.result = "won" 
    that_session.end_time = DiscoveryEndSessionData.ended
    that_session.status = "ended"

    attempts = len(session.query(UserTries).filter_by(session_id = DiscoveryEndSessionData.session_id).all())

    session.commit()

    return attempts