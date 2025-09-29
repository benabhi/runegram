# src/models/item.py

from sqlalchemy import BigInteger, Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base

class Item(Base):
    """
    Representa una instancia de un objeto en el mundo.
    """
    __tablename__ = 'items'

    id = Column(BigInteger, primary_key=True)

    # 'key' es el identificador único que nos enlaza con el prototipo en item_prototypes.py
    key = Column(String(50), nullable=False, index=True)

    # Estos campos son para overrides. Si son NULL, se usa el valor del prototipo.
    # Esto permite objetos únicos (ej: "la espada corta de Elara").
    name_override = Column(String(100), nullable=True)
    description_override = Column(Text, nullable=True)

    # --- Ubicación del objeto ---
    room_id = Column(BigInteger, ForeignKey('rooms.id'), nullable=True)
    character_id = Column(BigInteger, ForeignKey('characters.id'), nullable=True)

    # Relaciones para acceder fácilmente
    room = relationship("src.models.room.Room", back_populates="items")
    character = relationship("src.models.character.Character", back_populates="items")