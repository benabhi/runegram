# src/models/item.py
"""
Módulo que define el Modelo de Datos para una Instancia de Objeto (Item).

Este archivo contiene la clase `Item`, que se mapea a la tabla `items`.
Es fundamental entender que este modelo NO representa un tipo de objeto, sino
una INSTANCIA única de un objeto en el mundo.

Este modelo es deliberadamente "ligero". La mayoría de sus propiedades (nombre,
descripción, scripts, etc.) no se almacenan en la base de datos, sino que se
obtienen en tiempo de ejecución a través de la columna `key`, que lo vincula
a su prototipo correspondiente en `game_data/item_prototypes.py`.
"""

from sqlalchemy import BigInteger, Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from game_data.item_prototypes import ITEM_PROTOTYPES
from .base import Base

class Item(Base):
    """
    Representa una instancia de un objeto en el mundo del juego.
    """
    __tablename__ = 'items'

    # --- Atributos de la Instancia ---

    id = Column(BigInteger, primary_key=True)

    # La clave que vincula esta instancia con su prototipo en ITEM_PROTOTYPES.
    # Por ejemplo: "espada_viviente".
    key = Column(String(50), nullable=False, index=True)

    # Atributos `_override`: Permiten que una instancia específica tenga
    # un nombre o descripción diferente a la de su prototipo, creando objetos únicos.
    # Si son `NULL`, se usarán los valores del prototipo.
    name_override = Column(String(100), nullable=True)
    description_override = Column(Text, nullable=True)

    # --- Ubicación del Objeto ---

    # El ID de la sala donde se encuentra el objeto.
    # Es `NULL` si el objeto está en el inventario de un personaje.
    room_id = Column(BigInteger, ForeignKey('rooms.id'), nullable=True)

    # El ID del personaje que lleva el objeto.
    # Es `NULL` si el objeto está en el suelo de una sala.
    character_id = Column(BigInteger, ForeignKey('characters.id'), nullable=True)

    # --- Relaciones de SQLAlchemy ---

    # Relación muchos-a-uno con la sala. Permite acceder a `item.room`.
    room = relationship("Room", back_populates="items")

    # Relación muchos-a-uno con el personaje. Permite acceder a `item.character`.
    character = relationship("Character", back_populates="items")

    @property
    def prototype(self) -> dict:
        """
        Propiedad de conveniencia que devuelve el diccionario del prototipo
        para este objeto desde `game_data`. Es el puente entre la instancia
        de la base de datos y su definición de contenido.
        """
        return ITEM_PROTOTYPES.get(self.key, {})

    def get_name(self) -> str:
        """
        Obtiene el nombre del item.
        Prioriza el `name_override` si existe; de lo contrario,
        recurre al nombre definido en el prototipo.
        """
        return self.name_override or self.prototype.get("name", "un objeto misterioso")

    def get_description(self) -> str:
        """
        Obtiene la descripción del item.
        Prioriza el `description_override` si existe; de lo contrario,
        recurre a la descripción definida en el prototipo.
        """
        return self.description_override or self.prototype.get("description", "No tiene nada de especial.")

    def get_keywords(self) -> list[str]:
        """
        Obtiene las palabras clave del item, que siempre provienen del prototipo.
        """
        return self.prototype.get("keywords", [])

    def __repr__(self):
        """
        Representación en string del objeto, útil para logging y depuración.
        """
        return f"<Item(id={self.id}, key='{self.key}')>"