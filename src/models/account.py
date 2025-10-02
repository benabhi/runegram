# src/models/account.py
"""
Módulo que define el Modelo de Datos para una Cuenta de Usuario.

Este archivo contiene la clase `Account`, que se mapea a la tabla `accounts`
en la base de datos. Una cuenta representa a un usuario real a nivel de aplicación,
identificado de forma única por su `telegram_id`.

La cuenta es la entidad "propietaria" de un personaje (`Character`) y almacena
metadatos sobre el usuario, como su rol (JUGADOR, ADMIN, SUPERADMIN) y su estado
(ACTIVE, BLOCKED).
"""

from sqlalchemy import BigInteger, Column, String, Integer
from sqlalchemy.orm import relationship

from .base import Base

class Account(Base):
    """
    Representa una cuenta de usuario en la base de datos.
    """
    __tablename__ = 'accounts'

    # Identificador único de la cuenta en nuestra base de datos.
    id = Column(Integer, primary_key=True, autoincrement=True)

    # El ID de usuario único proporcionado por Telegram.
    # Es crucial para vincular nuestra cuenta interna con el usuario de Telegram.
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)

    # El rol del usuario en el juego. Determina el acceso a comandos especiales.
    # Jerarquía de roles (de mayor a menor): SUPERADMIN > ADMIN > JUGADOR.
    role = Column(String, default='JUGADOR', nullable=False, server_default='JUGADOR')

    # El estado de la cuenta (ej: 'ACTIVE', 'BLOCKED').
    # Permite gestionar el acceso de los usuarios a nivel de cuenta.
    status = Column(String(20), default='ACTIVE', nullable=False, server_default='ACTIVE')

    # --- Relaciones de SQLAlchemy ---

    # Relación uno-a-uno con el personaje del juego.
    # `uselist=False` indica que una cuenta solo puede tener un personaje.
    # `back_populates` asegura que la relación sea bidireccional.
    character = relationship("Character", back_populates="account", uselist=False)

    def __repr__(self):
        """
        Representación en string del objeto, útil para logging y depuración.
        """
        return f"<Account(id={self.id}, telegram_id={self.telegram_id}, role='{self.role}')>"