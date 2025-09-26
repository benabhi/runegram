# src/commands/command.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.character import Character

class Command:
    """Clase base para todos los comandos del juego."""
    names: list[str] = []  # Alias del comando, ej: ["mirar", "m"]
    lock: str = ""         # El string de lock para este comando

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        """El método que se ejecuta cuando se llama al comando."""
        raise NotImplementedError