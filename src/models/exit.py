# src/models/exit.py

from sqlalchemy import BigInteger, Column, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class Exit(Base):
    """
    Representa una salida unidireccional desde una sala a otra.
    """
    __tablename__ = 'exits'

    id = Column(BigInteger, primary_key=True)

    # El nombre que el jugador escribe para usar la salida (ej: "norte", "puerta de roble")
    name = Column(String(50), nullable=False, index=True)

    # De qué sala parte esta salida
    from_room_id = Column(BigInteger, ForeignKey('rooms.id'), nullable=False)
    # A qué sala lleva esta salida
    to_room_id = Column(BigInteger, ForeignKey('rooms.id'), nullable=False)

    # El string de lock para esta salida específica
    locks = Column(String, nullable=False, default="")

    # Relación para poder acceder a la sala de origen
    from_room = relationship("src.models.room.Room", foreign_keys=[from_room_id], back_populates="exits_from")

    # Relación para poder acceder a la sala de destino (útil para validaciones)
    # --- LÍNEA MODIFICADA ---
    to_room = relationship("src.models.room.Room", foreign_keys=[to_room_id], back_populates="exits_to")