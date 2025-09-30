# src/models/account.py
from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import relationship

from .base import Base

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    role = Column(String, default='JUGADOR', nullable=False)

    # --- NUEVA COLUMNA AÑADIDA ---
    # Para estados persistentes como 'ACTIVE', 'BLOCKED', etc.
    status = Column(String(20), default='ACTIVE', nullable=False, server_default='ACTIVE')

    # Relación: Una cuenta tiene un personaje
    character = relationship("src.models.character.Character", back_populates="account", uselist=False)

    def __repr__(self):
        return f"<Account(id={self.id}, telegram_id={self.telegram_id})>"