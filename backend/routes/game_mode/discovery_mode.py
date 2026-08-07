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
    
    new_session = DiscoverSession(
        id=str(uuid4()),
        number=engine.DiscoverMode.get_random(DiscoverData.max_range),
        status="abandoned",
        started_time = time.time(),
        ended_time = None,
        player_id = DiscoverData.player_id,
        type = "discover",
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

    that_session.status = "won" 
    that_session.end_time = DiscoveryEndSessionData.ended

    attempts = len(session.query(UserTries).filter_by(session_id = DiscoveryEndSessionData.session_id).all())

    session.commit()

    return attempts