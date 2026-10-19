# type: ignore
from fastapi import APIRouter , HTTPException
from all import *
import engine
from routes.utils import get_player_or_404 , get_owned_session , ensure_open
from routes.powerups import ITEM_LIFE , ITEM_MULTIPLIER , LIFE_BONUS

router = APIRouter(prefix="/classic")

MAX_LEVEL = 1000

@router.post("/level")
def get_level(lvlData: LevelData):
    player = get_player_or_404(lvlData.player_id)

    if not 1 <= lvlData.level <= MAX_LEVEL:
        raise HTTPException(status_code=422 , detail=f"level must be between 1 and {MAX_LEVEL}")
    if lvlData.level > player.level:
        raise HTTPException(status_code=403 , detail="Level not unlocked yet")

    instance = engine.SoloMode(lvlData.level)

    solo_sessson = SoloSession(
        id=str(uuid4()),
        number=instance.get_number(),
        status=GIVEN_UP,
        started_time = time.time(),
        ended_time = None,
        player_id = player.id,
        type = "solo",
        time_limit = instance.get_max_time(),
        max_attempt=instance.get_max_try(),
        attempt_left=instance.get_max_try(),
        max_range=lvlData.level*10,
    )
    session.add(solo_sessson)
    session.commit()

    return SoloModeResponse(
        session_id= solo_sessson.id,   
        max_attempt=solo_sessson.max_attempt, 
        max_range=lvlData.level*10,
        attempt_left=solo_sessson.attempt_left, 
        time_limit = solo_sessson.time_limit 
    )


@router.post("/end_level")
def SessionFinished(ClassicEndLevelData :ClassicEndLevelData):
    
    user = get_player_or_404(ClassicEndLevelData.player_id)
    that_session = get_owned_session(ClassicEndLevelData.session_id , user.id)
    if not isinstance(that_session , SoloSession):
        raise HTTPException(status_code=404 , detail="Session not found")
    ensure_open(that_session)

    if ClassicEndLevelData.status not in (WIN_STATE , LOSE_STATE):
        raise HTTPException(status_code=422 , detail="status must be 'win' or 'lose'")

    # le temps est mesure cote serveur, jamais fourni par le client
    ended = time.time()
    time_used = ended - that_session.started_time

    if ClassicEndLevelData.status == LOSE_STATE:
        that_session.status = LOSE_STATE
        that_session.ended_time = ended
        session.commit()
        return SoloEndGameData(coins=0 , xp = 0 ,stars = 0)

    level = ClassicEndLevelData.level_played
    if not 1 <= level <= min(MAX_LEVEL , user.level):
        raise HTTPException(status_code=403 , detail="Invalid level")
    L = engine.SoloMode(level)
    # la session doit correspondre au niveau annonce
    # les essais bonus (power-up "Vie bonus") sont ajoutes a max_attempt: on les retire pour verifier le niveau
    extra_attempts = LIFE_BONUS * session.query(SessionPowerup).filter_by(session_id = that_session.id , item_id = ITEM_LIFE).count()
    if that_session.max_attempt - extra_attempts != L.get_max_try() or that_session.number > level*10:
        raise HTTPException(status_code=409 , detail="Session does not match this level")

    inputs = [t.number for t in session.query(UserTries).filter_by(session_id = that_session.id).all()]
    if that_session.number not in inputs:
        raise HTTPException(status_code=409 , detail="The number has not been found")

    coins = L.getRewardCoin(inputs , time_used , that_session.number)
    if session.query(SessionPowerup).filter_by(session_id = that_session.id , item_id = ITEM_MULTIPLIER).count():
        coins *= 2
    xp = L.getXP(inputs , time_used , that_session.number)
    stars = L.getStars(inputs , time_used , that_session.number)

    that_session.status = "won" 
    that_session.ended_time = ended
    user.xp += xp
    user.coins += coins
    user.gems += L.getDaimond(inputs , time_used , that_session.number)
    if user.level == level :
        user.level += 1

    session.commit()

    return SoloEndGameData(coins=coins , xp = xp , stars = stars)
