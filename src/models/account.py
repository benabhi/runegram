# src/models/account.py
"""
Módulo que define el Modelo de Datos para una Cuenta de Usuario.

Este archivo contiene la clase `Account`, que se mapea a la tabla `accounts`
en la base de datos. Una cuenta representa a un usuario real a nivel de aplicación,
identificado de forma única por su `telegram_id`.

La cuenta es la entidad "propietaria" de un personaje (`Character`) y almacena
metadatos sobre el usuario, como su rol (JUGADOR, ADMIN, SUPERADMIN) y su estado
(ACTIVE, BLOCKED).

Además, gestiona el sistema de baneos y apelaciones, permitiendo:
- Baneos permanentes o temporales con razón y auditoría
- Sistema de apelaciones (una oportunidad por cuenta)
- Trazabilidad completa (quién baneó, cuándo, por qué)
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

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

    # --- Sistema de Baneos ---

    # Indica si la cuenta está actualmente baneada
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, server_default='false', index=True)

    # Razón del ban proporcionada por el administrador (máximo 500 caracteres)
    ban_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Fecha y hora en que se aplicó el ban
    banned_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # ID de la cuenta del administrador que aplicó el ban
    banned_by_account_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=True
    )

    # Fecha de expiración del ban (None = permanente, datetime = temporal)
    ban_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # --- Sistema de Apelaciones ---

    # Indica si el usuario ya ha apelado su ban (solo una oportunidad)
    has_appealed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, server_default='false')

    # Texto de la apelación proporcionado por el jugador (máximo 1000 caracteres)
    appeal_text: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Fecha y hora en que se envió la apelación
    appealed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # --- Relaciones de SQLAlchemy ---

    # Relación uno-a-uno con el personaje del juego.
    # `uselist=False` indica que una cuenta solo puede tener un personaje.
    # `back_populates` asegura que la relación sea bidireccional.
    character = relationship("Character", back_populates="account", uselist=False)

    # Relación para rastrear qué administrador aplicó el ban
    # Esta es una relación auto-referencial (Account -> Account)
    banned_by: Mapped[Optional["Account"]] = relationship(
        "Account",
        foreign_keys=[banned_by_account_id],
        remote_side="Account.id",
        uselist=False
    )

    def __repr__(self):
        """
        Representación en string del objeto, útil para logging y depuración.
        """
        return f"<Account(id={self.id}, telegram_id={self.telegram_id}, role='{self.role}')>"