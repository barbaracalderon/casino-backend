from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    balance = Column(Float, default=0.0)
    
    transactions = relationship("Transaction", back_populates="player")
