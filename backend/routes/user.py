from fastapi import APIRouter  ,HTTPException
import engine.props as gen
from engine.db_handler import *
from all import *



router = APIRouter(prefix="/user")


@router.get("/new_player")
def new_player():
    user = Player(
            name = gen.getName() , 
            id =  str(uuid4()),
            level = 1,
            created_at = time.time(),
            xp = 0,
            coins = 500,
            gems = 5)
    
    session.add(user)
    

    for items_id in [d.id for d in session.query(Items).all()]:
        t = PlayerItems(playerId = user.id , itemId = items_id)
        session.add(t)

    session.commit()

    return PlayerData(id = user.id , name = user.name ,  # type: ignore
                      gems = user.gems , coins = user.coins , # type: ignore
                      xp = user.xp , level = user.level)# type: ignore

@router.get("/{user_id}")
def get_user(user_id : str):
    user = session.query(Player).filter_by(id = user_id).first()
    if not user:
        raise HTTPException(404 , "user not found")
    
    
    return PlayerData(id = user.id , name = user.name , gems = user.gems , coins = user.coins , xp = user.xp , level = user.level) # type: ignore # 

@router.post("/rename")
def editPlayer(editData : EditName):
    user = session.query(Player).filter_by(id = editData.player_id).first()
    if not user:
        raise HTTPException(404 , "user not found")
    
    user.name = editData.name

    return PlayerData(id = user.id , name = user.name , gems = user.gems , coins = user.coins , xp = user.xp , level = user.level) # type: ignore # 

@router.get("/stats/{user_id}")
def getStats(user_id: str):
    info = Statistics(user_id)
    return StatsData(fatestWin= float(info.getFastestTime()) , TotalTime = info.getTotalTime() ,
                     TotalTries = info.getNbTry(),meanTries =  info.getMeanTries() , 
                     winGames=info.getTotalWin() ,TotalGames = info.getTotalGames(),
                    endedGames = info.getTotalGameFinished() 
                )


@router.get("/stats/history/{user_id}")
def getStats(user_id: str):
    datas = CropTable(5)
    T = []
    for i,d in enumerate(datas):
        T.append({"id" : i , 
         "type": "classic" if d.attempt_left != -1 else "discovery",
        "result" : d.result,
        "attemps" : d.max_attempt - d.attempt_left if  d.attempt_left != -1 else None,
         "date": d.started_time })
        
    return T
    


