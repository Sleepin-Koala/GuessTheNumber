from pydantic import BaseModel 
from typing import Optional , Mapping



class GuessData(BaseModel):
    session_id: str
    player_id : str
    number: int

class PlayerData(BaseModel):
    id: Optional[str]
    name : Optional[str]
    gems: Optional[int]
    coins : Optional[int]
    xp: Optional[int]
    level : Optional[int]

class GameStartRequest(BaseModel):
    name: str
    player_id: str
    model: Optional[str] = "classic" 

class GameStartResponse(BaseModel):
    session_id: str
    max_attempt: int
    attempt_left: int
    max_range: int
    time_limit: Optional[int]
    
class SoloData(BaseModel):
    player_id: str
    level : int
     
class LevelData(BaseModel):
    level : int
    player_id : str
    
class GuessResponse(BaseModel):
    result: str
    attempt_left: int
    distance : float

class SessionEndResponse(BaseModel):
    session_id: str
    player_id : str
    ended: float
    status: str
    levelPlayed: int

class JoinData(BaseModel):
    player_id: str
    server_id : str

class VersusData(BaseModel):
    room_id : str
    player_1: PlayerData
    player_2 : PlayerData
    status: str
    PlayerPlaying : str

class EditName(BaseModel):
    player_id: str
    name : str

class Discover(BaseModel):
    player_id : str
    max_range : int

class BuyData(BaseModel):
    playerId : str
    itemId : int

class StatsData(BaseModel):
    fatestWin : float
    TotalTime : float
    TotalTries: int
    meanTries : int 
    winGames: int
    TotalGames : int
    endedGames : int
    
    





