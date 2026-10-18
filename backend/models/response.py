from typing import Optional , Mapping
from pydantic import BaseModel 


#endless
class EndlessModeResponse(BaseModel):
    session_id: str
    max_attempt: int
    attempt_left: int
    max_range: int
    bet: int
    stage: int
    coins : int

#discover
class DiscoverModeResponse(BaseModel):
    session_id: str
    max_range: int


#solo

class SoloModeResponse(BaseModel):
    session_id: str
    max_attempt: int
    attempt_left: int
    max_range: int
    time_limit: int


class GuessResponse(BaseModel):
    result: str
    attempt_left: int
    max_attempt: int
    distance : float
    type: str


class StatsData(BaseModel):
    fatestWin: Optional[float] = None
    TotalTime: float
    TotalTries: int
    meanTries: float
    winGames: int
    TotalGames: int
    endedGames: int


class HistoryEntry(BaseModel):
    id: int
    type: str
    result: str
    attemps: Optional[int] = None
    date: float
