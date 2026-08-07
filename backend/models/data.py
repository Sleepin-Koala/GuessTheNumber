from pydantic import BaseModel 
from typing import Any, Optional


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


# Discovery

class DiscoverData(BaseModel):
    player_id : str
    max_range : int

class DiscoveryEndSessionData(BaseModel):
    session_id: str
    player_id: str
    ended: float



# Solo

     
class LevelData(BaseModel):
    level : int
    player_id : str

class ClassicEndLevelData(BaseModel):
    session_id: str
    player_id: str
    status: str
    level_played: int
    ended: float

# endless

class EndlessEndSessionData(BaseModel):
    session_id: str
    player_id: str
    status: str
    ended: float

class EndlessData(BaseModel):
    player_id: str
    bet: int
    stage : int

class RoomData(BaseModel) :
    room_id: str
    host_id: str
    guest_id : Optional[str]
    room_name : str
    bet_amount: int
    status: str
    max_range : int
    current_hider_id : Optional[str]
    current_guesser_id : Optional[str]
    last_distance:  Optional[float]
    last_feedback: Optional[str]
    round1_attempts_used : Optional[int]
    round2_attempts_used : Optional[int]
    winner_id : Optional[str]

class HostRoomData(BaseModel) :
    host_id: str
    name : str
    amount: int
    max_range : int

class CheckRoomData(BaseModel):
    room_id : str

class JoinData(BaseModel):
    player_id: str
    room_id : str

class HidenGuessNumberData(BaseModel):
    player_id : str
    number: int
