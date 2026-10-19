 # type: ignore
import engine
from all import *
from fastapi import APIRouter , HTTPException
from routes.utils import get_player_or_404 , get_owned_session , ensure_open

router = APIRouter(prefix="/discovery")

MAX_DISCOVERY_RANGE = 100_000


@router.post("/start")
def start_discovery(DiscoverData: DiscoverData):
    player = get_player_or_404(DiscoverData.player_id)

    if not 1 <= DiscoverData.max_range <= MAX_DISCOVERY_RANGE:
        raise HTTPException(status_code=422 , detail=f"max_range must be between 1 and {MAX_DISCOVERY_RANGE}")
    
    new_session = DiscoverSession(
        id=str(uuid4()),
        number=engine.DiscoverMode.get_random(DiscoverData.max_range),
        status=GIVEN_UP,
        started_time = time.time(),
        ended_time = None,
        player_id = player.id,
        type = "discover",
        max_range = DiscoverData.max_range,
    )
    
    session.add(new_session)
    session.commit()
    
    
    return DiscoverModeResponse(
        session_id = new_session.id,   
        max_range = DiscoverData.max_range,
    )


@router.post("/end_session")
def SessionFinished(DiscoveryEndSessionData :DiscoveryEndSessionData):
    
    get_player_or_404(DiscoveryEndSessionData.player_id)
    that_session = get_owned_session(DiscoveryEndSessionData.session_id , DiscoveryEndSessionData.player_id)
    if not isinstance(that_session , DiscoverSession):
        raise HTTPException(status_code=404 , detail="Session not found")
    ensure_open(that_session)

    tries = session.query(UserTries).filter_by(session_id = that_session.id).all()
    if not any(t.number == that_session.number for t in tries):
        raise HTTPException(status_code=409 , detail="The number has not been found yet")

    that_session.status = "won" 
    that_session.ended_time = time.time()

    session.commit()

    return len(tries)
