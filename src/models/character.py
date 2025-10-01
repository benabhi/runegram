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

    # Identificador único del personaje en nuestra base de datos.
    id = Column(BigInteger, primary_key=True)

    # El nombre del personaje, que debe ser único en todo el juego.
    name = Column(String(50), unique=True, nullable=False)

    # --- Claves Foráneas ---

    # Vínculo a la cuenta propietaria de este personaje.
    account_id = Column(BigInteger, ForeignKey('accounts.id'), nullable=False, unique=True)

    # Vínculo a la sala donde se encuentra actualmente el personaje.
    room_id = Column(BigInteger, ForeignKey('rooms.id'), nullable=False)

    # --- Atributos de Juego (Datos Estructurados) ---

    # Almacena la lista de CommandSets base que el personaje conoce.
    # Por ejemplo: ["general", "interaction", "movement", "channels"].
    # Este campo es la base para el sistema de comandos dinámicos.
    command_sets = Column(
        JSONB,
        nullable=False,
        server_default='["general", "interaction", "movement", "channels"]',
        default=["general", "interaction", "movement", "channels"]
    )

    # --- Relaciones de SQLAlchemy ---

    # Relación uno-a-uno con la cuenta.
    # Permite acceder al objeto `Account` desde el personaje vía `character.account`.
    account = relationship("Account", back_populates="character")

    # Relación muchos-a-uno con la sala.
    # Permite acceder al objeto `Room` desde el personaje vía `character.room`.
    room = relationship("Room")

    # Relación uno-a-muchos con los objetos del inventario.
    # Permite acceder a una lista de objetos `Item` vía `character.items`.
    items = relationship("Item", back_populates="character")

    # Relación uno-a-uno con las configuraciones del personaje.
    # Permite acceder al objeto `CharacterSetting` vía `character.settings`.
    # `cascade="all, delete-orphan"` asegura que si se borra un personaje,
    # su fila de configuraciones asociada también se borre automáticamente.
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