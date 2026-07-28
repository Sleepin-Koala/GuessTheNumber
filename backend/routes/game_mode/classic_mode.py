# type: ignore
from fastapi import APIRouter
from all import *
import engine

router = APIRouter(prefix="/classic")

@router.post("/level")
def get_level(lvlData: LevelData):

    player = session.query(Player).filter_by(id = lvlData.player_id).first()
    if not player:
        return

    instance = engine.SoloMode(lvlData.level)

    
    if player.level >= lvlData.level:

        solo_sessson = GameSession(
            id=str(uuid4()),
            max_attempt=instance.get_max_try(),
            attempt_left=instance.get_max_try(),
            number=instance.get_number(),
            status="continued",
            started_time = time.time(),
            end_time = 0,
            player_id = player.id,
            type = "solo",
            time_limit = instance.get_max_time(),
            result = GIVEN_UP
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
    
    that_session = session.query(GameSession).filter_by(id = ClassicEndLevelData.session_id).first()
    user = session.query(Player).filter_by(id = ClassicEndLevelData.player_id).first()  
    if not user or not that_session or not session:
        return
    
    actual_xp = user.xp
    actual_coins = user.coins
    actual_gems = user.gems
    
    if ClassicEndLevelData.status == WIN_STATE: 
        L = engine.SoloMode(ClassicEndLevelData.level_played)

        that_session.result = "won" 
        inputs = [i.number for i in session.query(UserTries).filter_by(session_id = that_session.id).all()]

        actual_xp += L.getXP( inputs , ClassicEndLevelData.ended-that_session.started_time ,that_session.number)
        actual_coins += L.getRewardCoin(inputs , ClassicEndLevelData.ended-that_session.started_time ,that_session.number)
        actual_gems += L.getDaimond(inputs , ClassicEndLevelData.ended-that_session.started_time ,that_session.number)

        if user.level == ClassicEndLevelData.level_played :
            user.level+=1

    if ClassicEndLevelData.status == LOSE_STATE:
        that_session.result = LOSE_STATE

    user.xp = actual_xp
    user.coins = actual_coins
    user.gems = actual_gems

    that_session.end_time = ClassicEndLevelData.ended
    that_session.status = "ended"
        

    session.commit()

    return PlayerData(id = user.id , name = user.name , gems = user.gems , coins = user.coins , xp = user.xp , level = user.level)  # 
   