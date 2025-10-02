# src/models/exit.py
"""
Módulo que define el Modelo de Datos para una Salida entre Salas.

Este archivo contiene la clase `Exit`, que se mapea a la tabla `exits`.
Cada fila en esta tabla representa una conexión UNIDIRECCIONAL desde una sala
de origen (`from_room_id`) hacia una sala de destino (`to_room_id`).

Una conexión bidireccional (ej: una puerta entre la sala A y la sala B) se
representa como dos filas separadas en esta tabla:
1. Una salida desde A hacia B (ej: "norte").
2. Una salida desde B hacia A (ej: "sur").
"""

from sqlalchemy import BigInteger, Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from .base import Base

class Exit(Base):
    """
    Representa una salida unidireccional desde una sala a otra.
    """
    __tablename__ = 'exits'

    # --- Atributos Principales ---

    id = Column(Integer, primary_key=True, autoincrement=True)

    # El nombre que el jugador escribe para usar la salida (ej: "norte", "puerta").
    name = Column(String(50), nullable=False, index=True)

    # El string de permisos para esta salida específica.
    locks = Column(String, nullable=False, default="")

    # --- Claves Foráneas ---

    # El ID de la sala desde la que parte esta salida.
    from_room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)

    # El ID de la sala a la que lleva esta salida.
    to_room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)

    # --- Relaciones de SQLAlchemy ---

    # Relación para poder acceder al objeto `Room` de origen.
    # `foreign_keys=[from_room_id]` es necesario para que SQLAlchemy sepa cuál de
    # las dos claves foráneas a 'rooms.id' debe usar para esta relación.
    # `back_populates="exits_from"` la conecta con la lista de salidas en el modelo Room.
    from_room = relationship("Room", foreign_keys=[from_room_id], back_populates="exits_from")

    # Relación para poder acceder al objeto `Room` de destino.
    # `back_populates="exits_to"` la conecta con la lista de "llegadas" en el modelo Room.
    to_room = relationship("Room", foreign_keys=[to_room_id], back_populates="exits_to")

    def __repr__(self):
        """
        Representación en string del objeto, útil para logging y depuración.
        """
        return f"<Exit(id={self.id}, name='{self.name}', from={self.from_room_id}, to={self.to_room_id})>"