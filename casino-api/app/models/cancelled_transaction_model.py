from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from app.db import Base

class CancelledTransaction(Base):
    __tablename__ = "cancelled_transactions"

    id = Column(Integer, primary_key=True, index=True)
    txn_uuid = Column(String, unique=True, index=True, nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"))
    value_bet = Column(Float, default=0.0)
    rolled_back = Column(Boolean, default=False)
