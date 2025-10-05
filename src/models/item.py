# src/models/item.py
"""
Módulo que define el Modelo de Datos para una Instancia de Objeto (Item).

Este archivo contiene la clase `Item`, que se mapea a la tabla `items`.
Representa una INSTANCIA única de un objeto en el mundo.

Este modelo es deliberadamente "ligero". La mayoría de sus propiedades se
obtienen en tiempo de ejecución a través de la columna `key`, que lo vincula
a su prototipo en `game_data/item_prototypes.py`.

Un `Item` también puede actuar como un contenedor para otros `Items` a través
de una relación de auto-referencia.
"""

from sqlalchemy import BigInteger, Column, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from game_data.item_prototypes import ITEM_PROTOTYPES
from .base import Base

class Item(Base):
    """
    Representa una instancia de un objeto en el mundo del juego.
    """
    __tablename__ = 'items'

    # --- Atributos de la Instancia ---

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), nullable=False, index=True)
    name_override = Column(String(100), nullable=True)
    description_override = Column(Text, nullable=True)

    # --- Datos de Tick Scripts ---
    # Almacena el estado de tracking para tick_scripts (cuándo se ejecutaron, etc.)
    tick_data = Column(JSONB, nullable=True, default=dict)

    # --- Ubicación del Objeto ---
    # Un objeto solo puede estar en una ubicación a la vez. Por lo tanto,
    # solo una de las siguientes tres columnas (`room_id`, `character_id`,
    # `parent_item_id`) debe tener un valor.

    # 1. En el suelo de una sala.
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)

    # 2. En el inventario de un personaje.
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=True)

    # 3. Dentro de otro objeto (contenedor).
    # Esta es una clave foránea que apunta a la misma tabla `items`.
    parent_item_id = Column(Integer, ForeignKey('items.id'), nullable=True)

    # --- Relaciones de SQLAlchemy ---

    # Relación con la sala donde se encuentra el objeto.
    room = relationship("Room", back_populates="items")

    # Relación con el personaje que lleva el objeto.
    character = relationship("Character", back_populates="items")

    # --- Relaciones de Contenedor (Auto-Referencia) ---

    # Relación para acceder al inventario de este objeto (si es un contenedor).
    # Es una lista de `Item` que tienen a este objeto como su `parent_item_id`.
    contained_items = relationship("Item", back_populates="parent_container", cascade="all, delete-orphan")

    # Relación para acceder al contenedor de este objeto (si está dentro de uno).
    # `remote_side=[id]` es necesario para que SQLAlchemy entienda la dirección
    # de esta relación de auto-referencia.
    parent_container = relationship("Item", back_populates="contained_items", remote_side=[id])


    @property
    def prototype(self) -> dict:
        """
        Devuelve el diccionario del prototipo para este objeto desde `game_data`.
        """
        return ITEM_PROTOTYPES.get(self.key, {})

    @property
    def category(self) -> str | None:
        """Retorna la categoría de este item desde su prototipo."""
        return self.prototype.get("category")

    @property
    def tags(self) -> list[str]:
        """Retorna los tags de este item desde su prototipo."""
        return self.prototype.get("tags", [])

    def get_name(self) -> str:
        """
        Obtiene el nombre del item, priorizando el `override` sobre el prototipo.
        """
        return self.name_override or self.prototype.get("name", "un objeto misterioso")

    def get_description(self) -> str:
        """
        Obtiene la descripción del item, priorizando el `override` sobre el prototipo.
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