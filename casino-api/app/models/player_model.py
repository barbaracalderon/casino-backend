from sqlalchemy import Column, Integer, String, Float
from app.db import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    balance = Column(Float, default=0.0)
