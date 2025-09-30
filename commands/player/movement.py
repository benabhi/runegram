# commands/player/movement.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import player_service, command_service # Importamos command_service
from src.utils.presenters import show_current_room

class CmdMove(Command):
    """
    Comando genérico para manejar todo el movimiento.
    """
    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        direction = self.names[0]
        target_exit = next(
            (exit_obj for exit_obj in character.room.exits_from if exit_obj.name == direction),
            None
        )

        if not target_exit:
            return await message.answer("No puedes ir en esa dirección.")

        await player_service.teleport_character(session, character.id, target_exit.to_room_id)

        # Después de movernos, actualizamos la lista de comandos de Telegram
        # ya que la nueva sala podría otorgar nuevos comandos.
        refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
        await command_service.update_telegram_commands(refreshed_character)

        await show_current_room(message)

# --- Creación del Command Set con descripciones ---
MOVEMENT_COMMANDS = [
    CmdMove(names=["norte", "n"], description="Moverse hacia el norte."),
    CmdMove(names=["sur", "s"], description="Moverse hacia el sur."),
    CmdMove(names=["este", "e"], description="Moverse hacia el este."),
    CmdMove(names=["oeste", "o"], description="Moverse hacia el oeste."),
    CmdMove(names=["arriba", "ar"], description="Moverse hacia arriba."),
    CmdMove(names=["abajo", "ab"], description="Moverse hacia abajo."),
    CmdMove(names=["noreste", "ne"], description="Moverse hacia el noreste."),
    CmdMove(names=["noroeste", "no"], description="Moverse hacia el noroeste."),
    CmdMove(names=["sureste", "se"], description="Moverse hacia el sureste."),
    CmdMove(names=["suroeste", "so"], description="Moverse hacia el suroeste."),
]