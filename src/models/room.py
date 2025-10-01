# src/models/room.py
"""
Módulo que define el Modelo de Datos para una Sala del Mundo.

Este archivo contiene la clase `Room`, que se mapea a la tabla `rooms`.
Cada fila en esta tabla representa una ubicación única en el juego.

Siguiendo la filosofía de diseño del motor, una `Room` en la base de datos
es principalmente una instancia que se corresponde con un prototipo definido en
`game_data/room_prototypes.py`, vinculado a través de la columna `key`.
"""

from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.orm import relationship

from .base import Base
from game_data.room_prototypes import ROOM_PROTOTYPES

class Room(Base):
    """
    Representa una sala o ubicación en el mundo del juego.
    """
    __tablename__ = 'rooms'

    # --- Atributos de la Instancia ---

    id = Column(BigInteger, primary_key=True)

    # La clave que vincula esta instancia con su prototipo en ROOM_PROTOTYPES.
    # Por ejemplo: "plaza_central". Es único y no debería cambiar.
    key = Column(String(50), unique=True, nullable=True, index=True)

    # El nombre y la descripción pueden ser actualizados desde los prototipos
    # por el `world_loader_service`.
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False, default="Esta es una sala sin describir.")

    # String de permisos para la sala en sí (ej: para impedir la entrada).
    locks = Column(String, nullable=False, default="")

    # --- Relaciones de SQLAlchemy ---

    # Relación uno-a-muchos con los objetos que se encuentran en esta sala.
    # Permite acceder a una lista de `Item` vía `room.items`.
    items = relationship("Item", back_populates="room")

    # Relación uno-a-muchos con las salidas QUE PARTEN DESDE ESTA SALA.
    # Permite acceder a una lista de `Exit` vía `room.exits_from`.
    # `cascade="all, delete-orphan"` asegura que si se borra una sala,
    # todas sus salidas asociadas también se eliminen.
    exits_from = relationship(
        "Exit",
        foreign_keys="[Exit.from_room_id]",
        back_populates="from_room",
        cascade="all, delete-orphan"
    )

    # Relación uno-a-muchos con las salidas QUE LLEGAN A ESTA SALA.
    # Es útil para comprobaciones inversas (ej: "¿qué salas conectan aquí?").
    exits_to = relationship(
        "Exit",
        foreign_keys="[Exit.to_room_id]",
        back_populates="to_room",
        cascade="all, delete-orphan"
    )

    @property
    def prototype(self) -> dict:
        """
        Propiedad de conveniencia que devuelve el diccionario del prototipo
        para esta sala desde `game_data`.
        """
        if not self.key:
            return {}
        return ROOM_PROTOTYPES.get(self.key, {})

    def __repr__(self):
        """
        Representación en string del objeto, útil para logging y depuración.
        """
        return f"<Room(id={self.id}, key='{self.key}', name='{self.name}')>"