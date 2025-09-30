# commands/player/movement.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import player_service
from src.utils.presenters import show_current_room

class CmdMove(Command):
    """
    Comando genérico para manejar todo el movimiento.
    La dirección se determina por el primer nombre en la lista de alias.
    """
    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        # El nombre principal del comando (ej: "norte") es la dirección.
        direction = self.names[0]

        # Buscamos si existe una salida con ese nombre en la sala actual.
        target_exit = next(
            (exit_obj for exit_obj in character.room.exits_from if exit_obj.name == direction),
            None
        )

        if not target_exit:
            return await message.answer("No puedes ir en esa dirección.")

        # Aquí iría la lógica de locks de salida en el futuro.
        # Por ahora, simplemente movemos al personaje.

        await player_service.teleport_character(session, character.id, target_exit.to_room_id)
        # Mostramos la nueva sala al jugador.
        await show_current_room(message)

# --- Creación del Command Set ---
# Creamos una instancia de CmdMove para cada dirección y sus alias.
MOVEMENT_COMMANDS = [
    CmdMove(names=["norte", "n"]),
    CmdMove(names=["sur", "s"]),
    CmdMove(names=["este", "e"]),
    CmdMove(names=["oeste", "o"]),
    CmdMove(names=["arriba", "ar"]),
    CmdMove(names=["abajo", "ab"]),
    CmdMove(names=["noreste", "ne"]),
    CmdMove(names=["noroeste", "no"]),
    CmdMove(names=["sureste", "se"]),
    CmdMove(names=["suroeste", "so"]),
]