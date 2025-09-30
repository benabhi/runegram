# src/models/character_setting.py
from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base

class CharacterSetting(Base):
    __tablename__ = 'character_settings'

    # Usamos el character_id como clave primaria para forzar una relación 1 a 1.
    character_id = Column(BigInteger, ForeignKey('characters.id'), primary_key=True)

    # Columna JSONB para guardar una lista de los canales activos.
    # Ejemplo: {"active_channels": ["novato", "comercio"]}
    active_channels = Column(JSONB, nullable=False, server_default='{}')

    # Relación inversa para poder acceder desde el personaje
    character = relationship("src.models.character.Character", back_populates="settings")