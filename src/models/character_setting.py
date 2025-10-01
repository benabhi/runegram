# src/models/character_setting.py
"""
Módulo que define el Modelo de Datos para las Configuraciones de un Personaje.

Este archivo contiene la clase `CharacterSetting`, que se mapea a la tabla
`character_settings`. Esta tabla almacena configuraciones personalizables
para cada personaje, manteniendo el modelo `Character` principal más limpio.

El uso de una columna `JSONB` (`active_channels`) permite añadir futuras
configuraciones (ej: colores, flags de tutorial) sin necesidad de modificar
el esquema de la base de datos, lo que hace que el sistema sea muy flexible
y extensible.
"""

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base

class CharacterSetting(Base):
    """
    Representa una fila de configuraciones para un personaje específico.
    """
    __tablename__ = 'character_settings'

    # --- Clave Primaria y Foránea ---

    # Usamos el ID del personaje como clave primaria (`primary_key=True`).
    # Esto impone una relación estricta de uno-a-uno a nivel de base de datos:
    # no puede haber más de una fila de configuraciones por personaje.
    character_id = Column(BigInteger, ForeignKey('characters.id'), primary_key=True)

    # --- Atributos de Configuración ---

    # Columna JSONB para guardar una lista de los canales a los que el personaje
    # está suscrito. Usar JSONB es muy flexible.
    # Ejemplo de contenido: `{"active_channels": ["novato", "comercio"]}`
    active_channels = Column(JSONB, nullable=False, server_default='{}')

    # --- Relaciones de SQLAlchemy ---

    # Relación inversa uno-a-uno con el personaje.
    # Permite acceder al objeto `Character` desde la configuración vía `settings.character`.
    character = relationship("Character", back_populates="settings")

    def __repr__(self):
        """
        Representación en string del objeto, útil para logging y depuración.
        """
        return f"<CharacterSetting(character_id={self.character_id})>"