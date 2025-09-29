# src/commands/player/interaction.py

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

# La ruta a 'command' es correcta porque ambos están en el mismo nivel relativo a la raíz
from commands.command import Command
# La ruta a 'character' debe partir de la raíz del proyecto, que incluye 'src'
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
            return await message.answer("¿Qué quieres coger?")

        item_name_to_get = " ".join(args).lower()
        item_to_get = None

        # Buscamos el objeto en la sala, usando el nuevo método del modelo
        for item in character.room.items:
            if item_name_to_get in item.get_name().lower():
                item_to_get = item
                break

        if not item_to_get:
            return await message.answer("No ves eso por aquí.")

        await item_service.move_item_to_character(session, item_to_get.id, character.id)

        # Usamos el nuevo método para mostrar el nombre
        await message.answer(f"Has cogido: {item_to_get.get_name()}")


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

        # Buscamos el objeto en el inventario, usando el nuevo método
        for item in character.items:
            if item_name_to_drop in item.get_name().lower():
                item_to_drop = item
                break

        if not item_to_drop:
            return await message.answer("No llevas eso.")

        await item_service.move_item_to_room(session, item_to_drop.id, character.room_id)

        # Usamos el nuevo método para mostrar el nombre
        await message.answer(f"Has dejado: {item_to_drop.get_name()}")


# --- Exportación del Command Set ---
INTERACTION_COMMANDS = [
    CmdGet(),
    CmdDrop(),
]