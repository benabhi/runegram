# src/commands/admin/movement.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from src.commands.command import Command
from src.models.character import Character
from src.services import player_service
from src.utils.presenters import show_current_room

class CmdTeleport(Command):
    names = ["teleport", "tp"]
    lock = "rol(ADMINISTRADOR)"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            return await message.answer("Uso: /teleport [ID_sala]")

        try:
            to_room_id = int(args[0])
        except (ValueError, IndexError):
            return await message.answer("El ID de la sala debe ser un número.")

        try:
            await player_service.teleport_character(session, character.id, to_room_id)
            await message.answer(f"🚀 Teletransportado a la sala {to_room_id}.")
            await show_current_room(message)
        except Exception as e:
            await message.answer(f"❌ Error al teletransportar: {e}")

# --- Exportación del Command Set ---
ADMIN_MOVEMENT_COMMANDS = [CmdTeleport()]