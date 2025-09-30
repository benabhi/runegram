# src/models/room.py

from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.orm import relationship

from .base import Base

class Room(Base):
    __tablename__ = 'rooms'

    id = Column(BigInteger, primary_key=True)
    key = Column(String(50), unique=True, nullable=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False, default="Esta es una sala sin describir.")
    locks = Column(String, nullable=False, default="")

    # Relaciones existentes
    items = relationship("src.models.item.Item", back_populates="room")

    # --- RELACIONES PARA SALIDAS ---
    # Una lista de todas las salidas QUE PARTEN DE ESTA SALA.
    exits_from = relationship("src.models.exit.Exit", foreign_keys="[Exit.from_room_id]", back_populates="from_room", cascade="all, delete-orphan")

    # Una lista de todas las salidas QUE LLEGAN A ESTA SALA.
    # --- LÍNEA MODIFICADA ---
    exits_to = relationship("src.models.exit.Exit", foreign_keys="[Exit.to_room_id]", back_populates="to_room", cascade="all, delete-orphan")