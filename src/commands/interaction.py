# src/commands/interaction.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from src.commands.command import Command
from src.models.character import Character
from src.services import item_service


class CmdGet(Command):
    names = ["coger", "g"]
    lock = ""

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        if not args:
            await message.answer("¿Qué quieres coger?")
            return

        item_name_to_get = " ".join(args)
        item_to_get = None

        # Buscamos el objeto en la sala
        for item in character.room.items:
            if item_name_to_get.lower() in item.name.lower():
                item_to_get = item
                break

        if not item_to_get:
            return await message.answer("No ves eso por aquí.")

        # Movemos el objeto usando el servicio
        await item_service.move_item_to_character(session, item_to_get.id, character.id)
        await message.answer(f"Has cogido: {item_to_get.name}")


class CmdDrop(Command):
    names = ["dejar", "d"]
    lock = ""

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        if not args:
            await message.answer("¿Qué quieres dejar?")
            return

        item_name_to_drop = " ".join(args)
        item_to_drop = None

        # Buscamos el objeto en el inventario del personaje
        for item in character.items:
            if item_name_to_drop.lower() in item.name.lower():
                item_to_drop = item
                break

        if not item_to_drop:
            return await message.answer("No llevas eso.")

        # Movemos el objeto usando el servicio
        await item_service.move_item_to_room(session, item_to_drop.id, character.room_id)
        await message.answer(f"Has dejado: {item_to_drop.name}")


# --- Lista de Comandos para el CommandSet "Interaction" ---
INTERACTION_COMMANDS = [
    CmdGet(),
    CmdDrop(),
]