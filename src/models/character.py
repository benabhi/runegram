# src/models/character.py
"""
Módulo que define el Modelo de Datos para un Personaje del Juego.

Este archivo contiene la clase `Character`, que se mapea a la tabla `characters`
en la base de datos. Un personaje es el "avatar" o la entidad con la que un
jugador interactúa dentro del mundo de Runegram.

El personaje está vinculado a una `Account` (el usuario real) y actúa como el
punto central para las relaciones de juego, como su ubicación (`Room`), su
inventario (`Item`), y sus configuraciones (`CharacterSetting`).
"""

from sqlalchemy import BigInteger, Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base

class Character(Base):
    """
    Representa un personaje jugable en la base de datos.
    """
    __tablename__ = 'characters'

    # --- Atributos Principales ---
    id = Column(BigInteger, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    # --- Claves Foráneas ---
    account_id = Column(BigInteger, ForeignKey('accounts.id'), nullable=False, unique=True)
    room_id = Column(BigInteger, ForeignKey('rooms.id'), nullable=False)

    # --- Atributos de Juego (Datos Estructurados) ---

    # Almacena la lista de CommandSets base que el personaje conoce.
    # Este campo es la base para el sistema de comandos dinámicos.
    command_sets = Column(
        JSONB,
        nullable=False,

        # Añadimos "dynamic_channels" y "settings" a la lista de sets por defecto
        # para que todos los jugadores tengan acceso a ellos desde el principio.
        server_default='["general", "interaction", "movement", "channels", "dynamic_channels", "settings"]',
        default=["general", "interaction", "movement", "channels", "dynamic_channels", "settings"]
    )

    # --- Relaciones de SQLAlchemy ---
    account = relationship("Account", back_populates="character")
    room = relationship("Room")
    items = relationship("Item", back_populates="character")
    settings = relationship(
        "CharacterSetting",
        back_populates="character",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        """
        Representación en string del objeto, útil para logging y depuración.
        """
        return f"<Character(id={self.id}, name='{self.name}')>"