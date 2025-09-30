# src/commands/admin/building.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from commands.command import Command
from src.models.character import Character
from src.services import item_service
from game_data.item_prototypes import ITEM_PROTOTYPES

class CmdGenerarObjeto(Command):
    names = ["generarobjeto", "genobj"]
    lock = "rol(ADMINISTRADOR)"
    description = "Genera un objeto en la sala a partir de su clave de prototipo."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            return await message.answer("Uso: /generarobjeto [key_del_prototipo]")

        item_key = args[0].lower()
        try:
            item = await item_service.spawn_item_in_room(session, character.room_id, item_key)
            item_name = ITEM_PROTOTYPES.get(item.key, {}).get("name", "un objeto desconocido")
            await message.answer(f"✅ Objeto '{item_name}' generado en la sala actual.")
        except ValueError as e:
            await message.answer(f"❌ Error: {e}")

# Exportamos el nuevo set de comandos de "spawning"
SPAWN_COMMANDS = [
    CmdGenerarObjeto(),
    # Aquí podrías añadir /generarnpc en el futuro
]