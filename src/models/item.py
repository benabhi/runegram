# src/models/item.py

from sqlalchemy import BigInteger, Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from game_data.item_prototypes import ITEM_PROTOTYPES # <-- Importa los prototipos

from .base import Base

class Item(Base):
    """
    Representa una instancia de un objeto en el mundo.
    """
    __tablename__ = 'items'

    id = Column(BigInteger, primary_key=True)
    key = Column(String(50), nullable=False, index=True)
    name_override = Column(String(100), nullable=True)
    description_override = Column(Text, nullable=True)
    room_id = Column(BigInteger, ForeignKey('rooms.id'), nullable=True)
    character_id = Column(BigInteger, ForeignKey('characters.id'), nullable=True)

    room = relationship("src.models.room.Room", back_populates="items")
    character = relationship("src.models.character.Character", back_populates="items")

    @property
    def prototype(self):
        """Devuelve el diccionario del prototipo para este objeto."""
        return ITEM_PROTOTYPES.get(self.key, {})

    def get_name(self) -> str:
        """Obtiene el nombre del item, usando override o el prototipo."""
        return self.name_override or self.prototype.get("name", "un objeto misterioso")

    def get_description(self) -> str:
        """Obtiene la descripción del item, usando override o el prototipo."""
        return self.description_override or self.prototype.get("description", "No tiene nada de especial.")

    def get_keywords(self) -> list[str]:
        """Obtiene las keywords del item desde el prototipo."""
        return self.prototype.get("keywords", [])