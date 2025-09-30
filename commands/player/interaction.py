# commands/player/interaction.py

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import item_service, command_service, player_service


class CmdGet(Command):
    names = ["coger", "g"]
    lock = ""
    description = "Recoge un objeto del suelo."

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        if not args:
            return await message.answer("¿Qué quieres coger?")

        item_name_to_get = " ".join(args).lower()
        item_to_get = None

        for item in character.room.items:
            if item_name_to_get in item.get_name().lower():
                item_to_get = item
                break

        if not item_to_get:
            return await message.answer("No ves eso por aquí.")

        await item_service.move_item_to_character(session, item_to_get.id, character.id)

        # Si el objeto que cogimos otorga un command set, actualizamos la lista en Telegram.
        if item_to_get.prototype.get("grants_command_sets"):
            refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
            await command_service.update_telegram_commands(refreshed_character)

        await message.answer(f"Has cogido: {item_to_get.get_name()}")


class CmdDrop(Command):
    names = ["dejar", "d"]
    lock = ""
    description = "Deja un objeto de tu inventario en el suelo."

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        if not args:
            return await message.answer("¿Qué quieres dejar?")

        item_name_to_drop = " ".join(args).lower()
        item_to_drop = None

        for item in character.items:
            if item_name_to_drop in item.get_name().lower():
                item_to_drop = item
                break

        if not item_to_drop:
            return await message.answer("No llevas eso.")

        await item_service.move_item_to_room(session, item_to_drop.id, character.room_id)

        # Si el objeto que dejamos otorgaba un command set, actualizamos la lista en Telegram.
        if item_to_drop.prototype.get("grants_command_sets"):
            refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
            await command_service.update_telegram_commands(refreshed_character)

        await message.answer(f"Has dejado: {item_to_drop.get_name()}")


# --- Exportación del Command Set ---
INTERACTION_COMMANDS = [
    CmdGet(),
    CmdDrop(),
]