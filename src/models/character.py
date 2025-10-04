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

from sqlalchemy import BigInteger, Column, String, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base

# Usar JSONB para PostgreSQL, JSON para otros (ej: SQLite en tests)
# JSONB es más eficiente en PostgreSQL pero JSON funciona en ambos
JSONType = JSON

class Character(Base):
    """
    Representa un personaje jugable en la base de datos.
    """
    __tablename__ = 'characters'

    # --- Atributos Principales ---
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    # --- Claves Foráneas ---
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, unique=True)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=False)

    # --- Atributos de Juego (Datos Estructurados) ---
    command_sets = Column(
        JSONType,
        nullable=False,
        server_default='["general", "character_creation", "interaction", "movement", "channels", "dynamic_channels", "settings"]',
        default=["general", "character_creation", "interaction", "movement", "channels", "dynamic_channels", "settings"]
    )

    # --- Relaciones de SQLAlchemy ---
    account = relationship("Account", back_populates="character")
    room = relationship("Room", back_populates="characters")
    items = relationship("Item", back_populates="character")
    settings = relationship(
        "CharacterSetting",
        back_populates="character",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def get_description(self) -> str:
        """
        Genera la descripción que otros ven al mirar a este personaje.

        Futuro: Esta función podría ser mucho más compleja, mostrando el equipo
        del personaje, su estado (luchando, durmiendo), etc. Los jugadores
        también podrían establecer su propia descripción personalizada.
        """
        # Por ahora, una descripción genérica.
        return f"Ves a {self.name}, un aventurero como tú. No parece tener nada de especial por el momento."

    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}')>"