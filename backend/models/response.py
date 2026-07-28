from typing import Optional , Mapping
from pydantic import BaseModel 


#endless
class EndlessModeResponse(BaseModel):
    session_id: str
    max_attempt: int
    attempt_left: int
    max_range: int
    time_limit: Optional[int]
    bet: int
    winnable: int
    stage: int

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
    distance : float
    type: str
