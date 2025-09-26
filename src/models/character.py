# src/models/character.py
from sqlalchemy import BigInteger, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base

class Character(Base):
    __tablename__ = 'characters'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # --- Relaciones ---
    account_id = Column(BigInteger, ForeignKey('accounts.id'), nullable=False, unique=True)
    account = relationship("src.models.account.Account", back_populates="character")

    room_id = Column(BigInteger, ForeignKey('rooms.id'), nullable=False)
    # Usamos el string 'src.models.room.Room'
    room = relationship("src.models.room.Room")

    # Usamos el string 'src.models.item.Item'
    items = relationship("src.models.item.Item", back_populates="character")

    command_sets = Column(JSONB, nullable=False, server_default='["general"]', default=["general"])