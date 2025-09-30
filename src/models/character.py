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
    room = relationship("src.models.room.Room")

    items = relationship("src.models.item.Item", back_populates="character")

    settings = relationship(
        "src.models.character_setting.CharacterSetting",
        back_populates="character",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # --- LÍNEA MODIFICADA ---
    # Actualizamos el valor por defecto para que todos los personajes nuevos
    # tengan acceso a todos los sets de comandos básicos desde el principio.
    command_sets = Column(
        JSONB,
        nullable=False,
        server_default='["general", "interaction", "movement", "channels"]',
        default=["general", "interaction", "movement", "channels"]
    )