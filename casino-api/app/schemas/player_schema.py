from pydantic import BaseModel
from typing import List

class PlayerResponse(BaseModel):
    id: int
    name: str
    balance: float

class PlayerCreate(BaseModel):
    name: str
    balance: float

class PlayersResponse(BaseModel):
    players: List[PlayerResponse]

    class Config:
        orm_mode = True

class PlayerUpdateRequest(BaseModel):
    name: str
    balance: float


class PlayerUpdateResponse(BaseModel):
    id: int
    name: str
    balance: float

