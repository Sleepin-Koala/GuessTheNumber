from fastapi import APIRouter  ,HTTPException
import engine.props as gen
from engine.db_handler import *
from all import *

import time


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

MAX_NAME_LENGTH = 20

@router.post("/rename")
def editPlayer(editData : RenameData):
    user = session.query(Player).filter_by(id = editData.player_id).first()
    if not user:
        raise HTTPException(404 , "user not found")

    name = editData.name.strip()
    if not 1 <= len(name) <= MAX_NAME_LENGTH:
        raise HTTPException(422 , f"name must be between 1 and {MAX_NAME_LENGTH} characters")

    user.name = name
    session.commit()

    return PlayerData(id = user.id , name = user.name , gems = user.gems , coins = user.coins , xp = user.xp , level = user.level) # type: ignore


@router.get("/stats/{user_id}")
def getStats(user_id: str):
    try:
        info = Statistics(user_id)
    except DataNotFound:
        raise HTTPException(404 , "user not found")

    return StatsData(fatestWin = info.getFastestTime() , TotalTime = info.getTotalTime() ,
                     TotalTries = info.getNbTry() , meanTries = info.getMeanTries() ,
                     winGames = info.getTotalWin() , TotalGames = info.getTotalGames() ,
                     endedGames = info.getTotalGameFinished())


@router.get("/stats/history/{user_id}")
def getHistory(user_id: str):
    try:
        info = Statistics(user_id)
    except DataNotFound:
        raise HTTPException(404 , "user not found")

    return info.getHistory(10)
