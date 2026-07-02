from fastapi import APIRouter 
from all import *
import engine

types = ["solo","discover"]


LEVELS = [{"level" : i , "exp" : 1000*i} for i in range(1 , 1000)]

GIVEN_UP = "abandoned"
LOSE_STATE = "lose"
WIN_STATE = "win"




router = APIRouter(prefix="/game")

@router.post("/discover")
def start_discovery(DiscoverData: Discover):

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
    
    
    return GameStartResponse(
        session_id= new_session.id,  # type: ignore 
        max_attempt=new_session.max_attempt, # type: ignore
        attempt_left=new_session.attempt_left, # type: ignore
        max_range = DiscoverData.max_range,
        time_limit = new_session.time_limit # type: ignore
    )

@router.post("/guess")
def guess(guessdata: GuessData):
    
    that_session = session.query(GameSession).filter_by(id=guessdata.session_id).first()
    if not that_session:
        return

    relation = UserTries(
        id = str(uuid4()),
        session_id  = that_session.id,
        number = guessdata.number,
        player_id = that_session.player.id if that_session.type != "multi" else guessdata.player_id
    )

    session.add(relation)

    
    if that_session.type == "solo":
        that_session.attempt_left -= 1

    session.commit()

    print(that_session.number)
    result = engine.checkResult(that_session.number , guessdata.number)

    distance = float(abs(that_session.number-guessdata.number))# pyright: ignore[reportArgumentType, reportCallIssue]

    return GuessResponse(result=result, attempt_left=that_session.attempt_left ,  # pyright: ignore[reportArgumentType]
                         distance = distance)     

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

    

        return GameStartResponse(
            session_id= solo_sessson.id,  # type: ignore 
            max_attempt=solo_sessson.max_attempt, # type: ignore
            max_range=lvlData.level*10,
            attempt_left=solo_sessson.attempt_left, # type: ignore
            time_limit = solo_sessson.time_limit # type: ignore
        )

@router.post("/endlevel")
def SessionFinished(EndResponse :SessionEndResponse):
    
    that_session = session.query(GameSession).filter_by(id = EndResponse.session_id).first()
    user = session.query(Player).filter_by(id = EndResponse.player_id).first()  
    if not user or not that_session or not session:
        return
    
    actual_xp = user.xp
    actual_coins = user.coins
    actual_gems = user.gems
    
    if EndResponse.status == WIN_STATE and that_session.type == "solo": # type: ignore
        L = engine.SoloMode(EndResponse.levelPlayed)

        that_session.result = "won" # type: ignore
        inputs = [i.number for i in session.query(UserTries).filter_by(session_id = that_session.id).all()]

        actual_xp += L.getXP( inputs , EndResponse.ended-that_session.started_time ,that_session.number)
        actual_coins += L.getRewardCoin(inputs , EndResponse.ended-that_session.started_time ,that_session.number)
        actual_gems += L.getDaimond(inputs , EndResponse.ended-that_session.started_time ,that_session.number)

        if user.level == EndResponse.levelPlayed :
            user.level+=1

    if EndResponse.status == LOSE_STATE:
        that_session.result = LOSE_STATE

    user.xp = actual_xp
    user.coins = actual_coins
    user.gems = actual_gems

    that_session.end_time = EndResponse.ended
    that_session.status = "ended"
        

    session.commit()

    return PlayerData(id = user.id , name = user.name , gems = user.gems , coins = user.coins , xp = user.xp , level = user.level) # type: ignore # 
