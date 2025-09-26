# src/models/room.py
from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base

class Room(Base):
    __tablename__ = 'rooms'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False, default="Esta es una sala sin describir.")
    exits = Column(JSONB, nullable=False, default={})
    locks = Column(String, nullable=False, default="")

    # Usamos el string 'src.models.item.Item'
    items = relationship("src.models.item.Item", back_populates="room")