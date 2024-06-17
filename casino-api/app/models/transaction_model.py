from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    txn_uuid = Column(String, unique=True, index=True, nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    value_bet = Column(Float, default=0.0)
    value_win = Column(Float, default=0.0)
    rolled_back = Column(Boolean, default=False)

    player = relationship("Player", back_populates="transactions")
