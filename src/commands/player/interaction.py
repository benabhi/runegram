# src/commands/player/interaction.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from src.commands.command import Command
from src.models.character import Character
from src.services import item_service

class CmdGet(Command):
    names = ["coger", "g"]
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            return await message.answer("¿Qué quieres coger?")

        item_name_to_get = " ".join(args)
        item_to_get = next((item for item in character.room.items if item_name_to_get.lower() in item.name.lower()), None)

        if not item_to_get:
            return await message.answer("No ves eso por aquí.")

        await item_service.move_item_to_character(session, item_to_get.id, character.id)
        await message.answer(f"Has cogido: {item_to_get.name}")

class CmdDrop(Command):
    names = ["dejar", "d"]
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            return await message.answer("¿Qué quieres dejar?")

        item_name_to_drop = " ".join(args)
        item_to_drop = next((item for item in character.items if item_name_to_drop.lower() in item.name.lower()), None)

        if not item_to_drop:
            return await message.answer("No llevas eso.")

        await item_service.move_item_to_room(session, item_to_drop.id, character.room_id)
        await message.answer(f"Has dejado: {item_to_drop.name}")

# --- Exportación del Command Set ---
INTERACTION_COMMANDS = [CmdGet(), CmdDrop()]