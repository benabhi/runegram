# src/commands/player/interaction.py

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import item_service
# Importamos la nueva función de ayuda para obtener el nombre real de un ítem
from src.utils.presenters import get_item_name


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
            return await message.answer("¿Qué quieres coger?")

        item_name_to_get = " ".join(args).lower()
        item_to_get = None

        # Buscamos el objeto en la sala, comparando con el nombre del prototipo
        for item in character.room.items:
            if item_name_to_get in get_item_name(item).lower():
                item_to_get = item
                break

        if not item_to_get:
            return await message.answer("No ves eso por aquí.")

        # Movemos el objeto usando el servicio
        await item_service.move_item_to_character(session, item_to_get.id, character.id)

        # Mostramos el nombre correcto del objeto cogido
        await message.answer(f"Has cogido: {get_item_name(item_to_get)}")


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
            return await message.answer("¿Qué quieres dejar?")

        item_name_to_drop = " ".join(args).lower()
        item_to_drop = None

        # Buscamos el objeto en el inventario del personaje
        for item in character.items:
            if item_name_to_drop in get_item_name(item).lower():
                item_to_drop = item
                break

        if not item_to_drop:
            return await message.answer("No llevas eso.")

        # Movemos el objeto usando el servicio
        await item_service.move_item_to_room(session, item_to_drop.id, character.room_id)

        # Mostramos el nombre correcto del objeto dejado
        await message.answer(f"Has dejado: {get_item_name(item_to_drop)}")


# --- Exportación del Command Set ---
INTERACTION_COMMANDS = [
    CmdGet(),
    CmdDrop(),
]