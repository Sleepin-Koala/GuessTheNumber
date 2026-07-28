from pydantic import BaseModel 


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

