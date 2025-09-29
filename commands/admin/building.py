# src/commands/admin/building.py

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import world_service, item_service, player_service


class CmdCreateRoom(Command):
    names = ["crearsala"]
    lock = "rol(ADMINISTRADOR)"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        room_name = " ".join(args)
        if not room_name:
            return await message.answer("Uso: /crearsala [nombre de la sala]")

        try:
            room = await world_service.create_room(session, room_name)
            await message.answer(f"✅ Sala '{room.name}' creada con éxito. ID: {room.id}")
        except Exception as e:
            await message.answer(f"❌ Error al crear la sala: {e}")

class CmdDescribeRoom(Command):
    names = ["describirsala"]
    lock = "rol(ADMINISTRADOR)"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        description = " ".join(args)
        if not description:
            return await message.answer("Uso: /describirsala [descripción de la sala]")

        await world_service.set_room_description(session, character.room_id, description)
        await message.answer(f"✅ Descripción de la sala actual (ID: {character.room_id}) actualizada.")

class CmdConnectRoom(Command):
    names = ["conectarsala"]
    lock = "rol(ADMINISTRADOR)"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if len(args) != 3 or args[1].lower() != 'a':
            return await message.answer("Uso: /conectarsala [dirección] a [ID_sala_destino]")

        direction, _, to_room_id_str = args
        try:
            to_room_id = int(to_room_id_str)
        except ValueError:
            return await message.answer("El ID de la sala de destino debe ser un número.")

        try:
            # Pasamos True explícitamente para el comportamiento bidireccional
            await world_service.link_rooms(session, character.room_id, direction, to_room_id, bidirectional=True)
            await message.answer(f"✅ Salida '{direction}' creada desde tu sala (ID: {character.room_id}) hacia la sala {to_room_id}.")
        except Exception as e:
            await message.answer(f"❌ Error al conectar las salas: {e}")


# --- NUEVO COMANDO AÑADIDO ---
class CmdCreateItem(Command):
    names = ["crearitem"]
    lock = "rol(ADMINISTRADOR)"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            return await message.answer("Uso: /crearitem [key_del_prototipo]")

        item_key = args[0].lower()

        try:
            item = await item_service.spawn_item_in_room(session, character.room_id, item_key)
            # Para mostrar el nombre correcto, necesitamos acceder al prototipo
            from game_data.item_prototypes import ITEM_PROTOTYPES
            item_name = ITEM_PROTOTYPES.get(item.key, {}).get("name", "un objeto desconocido")
            await message.answer(f"✅ Objeto '{item_name}' creado en la sala actual. ID de instancia: {item.id}")
        except ValueError as e:
            await message.answer(f"❌ Error: {e}")
        except Exception as e:
            await message.answer(f"❌ Error inesperado al crear el objeto: {e}")



# --- Exportación del Command Set (ACTUALIZADO) ---
BUILDING_COMMANDS = [
    CmdCreateRoom(),
    CmdDescribeRoom(),
    CmdConnectRoom(),
    CmdCreateItem(),
]