from pydantic import BaseModel
from typing import List, Optional


class TransactionCreate(BaseModel):
    player_id: int
    value_bet: float
    txn_uuid: str

class TransactionBalanceResponse(BaseModel):
    id: int
    player_id: int
    balance: float
    txn_uuid: str

class TransactionResponse(BaseModel):
    id: int
    txn_uuid: str
    player_id: int
    value_bet: Optional[float]
    value_win: Optional[float]

    class Config:
        orm_mode = True

class TransactionsResponse(BaseModel):
    transactions: List[TransactionResponse]

    class Config:
        orm_mode = True

class TransactionWin(BaseModel):
    player_id: int
    value_win: float
    txn_uuid: str

class TransactionCancelled(BaseModel):
    txn_uuid: str
    player_id: int
    value_bet: float

class TransactionBalanceUpdate(BaseModel):
    player_id: int
    balance: float
