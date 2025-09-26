# src/models/room.py
from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base

class Room(Base):
    __tablename__ = 'rooms'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False, default="Esta es una sala sin describir.")

    # Usamos JSONB para almacenar las salidas. Es flexible y eficiente.
    # Ejemplo: {"norte": 2, "cueva": 15}
    exits = Column(JSONB, nullable=False, default={})