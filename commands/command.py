# src/commands/command.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.character import Character

class Command:
    """Clase base para todos los comandos del juego."""
    # El lock puede seguir siendo un atributo de clase
    lock: str = ""

    def __init__(self, names: list[str] = None):
        """
        Inicializador para permitir la creación de instancias de comandos
        con alias dinámicos, como los comandos de movimiento.
        """
        # Si se pasan 'names' al crear la instancia, los usamos.
        # Si no, usamos los definidos en la clase (comportamiento antiguo).
        if names:
            self.names = names
        elif not hasattr(self, 'names'):
            self.names = []

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        """El método que se ejecuta cuando se llama al comando."""
        raise NotImplementedError