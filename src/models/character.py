# src/models/character.py
from sqlalchemy import BigInteger, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Character(Base):
    __tablename__ = 'characters'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # --- Relaciones existentes ---
    account_id = Column(BigInteger, ForeignKey('accounts.id'), nullable=False, unique=True)
    account = relationship("Account", back_populates="character")

    # --- NUEVA RELACIÓN ---
    # Un personaje está en una sala.
    room_id = Column(BigInteger, ForeignKey('rooms.id'), nullable=False)
    room = relationship("Room")