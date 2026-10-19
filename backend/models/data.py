from pydantic import BaseModel , Field
from typing import Any, Optional , Annotated


Id = Annotated[str, Field(min_length=1, max_length=64)]           # identifiants: courts
BigNumber = Annotated[int, Field(ge=-10**9, le=10**9)]            # evite les depassements d'entier SQLite
Coins = Annotated[int, Field(ge=0, le=10**9)]


class ClaimData(BaseModel):
    player_id: Id


class GuessData(BaseModel):
    session_id: Id
    player_id : Id
    number: BigNumber

class PlayerData(BaseModel):
    id: Optional[str]
    name : Optional[str]
    gems: Optional[int]
    coins : Optional[int]
    xp: Optional[int]
    level : Optional[int]

class SoloEndGameData(BaseModel):
    coins: int
    xp: int
    stars: int


# Discovery

class DiscoverData(BaseModel):
    player_id : Id
    max_range : Annotated[int, Field(ge=-10**9, le=10**9)]

class DiscoveryEndSessionData(BaseModel):
    session_id: Id
    player_id: Id
    ended: float



# Solo

     
class LevelData(BaseModel):
    level : Annotated[int, Field(ge=-10**6, le=10**6)]
    player_id : Id

class ClassicEndLevelData(BaseModel):
    session_id: Id
    player_id: Id
    status: Annotated[str, Field(max_length=16)]
    level_played: Annotated[int, Field(ge=-10**6, le=10**6)]
    ended: float

# endless

class EndlessEndSessionData(BaseModel):
    session_id: Id
    player_id: Id
    status: Annotated[str, Field(max_length=16)]
    ended: float

class EndlessData(BaseModel):
    player_id: Id
    bet: Annotated[int, Field(ge=-10**9, le=10**9)]
    stage : Annotated[int, Field(ge=-10**6, le=10**6)]

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
    host_name : Optional[str] = None
    guest_name : Optional[str] = None
    end_reason : Optional[str] = None       # pourquoi la partie s'est terminee
    turn_deadline : Optional[float] = None  # quand le joueur dont c'est le tour sera declare forfait (epoch, secondes)
    server_time : Optional[float] = None    # heure du serveur au moment de l'envoi (pour calculer le temps restant sans decalage d'horloge)

class LeaveData(BaseModel):
    player_id: Id

class HostRoomData(BaseModel) :
    host_id: Id
    name : Annotated[str, Field(max_length=60)]
    amount: Coins
    max_range : Annotated[int, Field(ge=1, le=10**6)]

class CheckRoomData(BaseModel):
    room_id : Id

class JoinData(BaseModel):
    player_id: Id
    room_id : Id

class HidenGuessNumberData(BaseModel):
    player_id : Id
    number: BigNumber


class RenameData(BaseModel):
    player_id: Id
    name: Annotated[str, Field(max_length=40)]

class PowerupData(BaseModel):
    session_id: Id
    player_id: Id
    item_id: Annotated[int, Field(ge=1, le=1000)]

class BuyData(BaseModel):
    playerId: Id
    itemId: Annotated[int, Field(ge=1, le=1000)]
