# src/models/item.py
from sqlalchemy import BigInteger, Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Item(Base):
    __tablename__ = 'items'

    id = Column(BigInteger, primary_key=True)
    key = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False, default="No tiene nada de especial.")

    room_id = Column(BigInteger, ForeignKey('rooms.id'), nullable=True)
    character_id = Column(BigInteger, ForeignKey('characters.id'), nullable=True)

    # Usamos strings para romper la dependencia circular
    room = relationship("src.models.room.Room", back_populates="items")
    character = relationship("src.models.character.Character", back_populates="items")