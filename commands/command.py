# commands/command.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.character import Character

class Command:
    """Clase base para todos los comandos del juego."""
    lock: str = ""
    description: str = "Un comando sin descripción."

    def __init__(self, names: list[str] = None, description: str = None):
        """
        Inicializador para permitir la creación de instancias de comandos
        con alias y descripciones dinámicas.
        """
        if names:
            self.names = names
        elif not hasattr(self, 'names'):
            self.names = []

        if description:
            self.description = description
        elif not hasattr(self, 'description'):
            self.description = "Un comando sin descripción."

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        """El método que se ejecuta cuando se llama al comando."""
        raise NotImplementedError