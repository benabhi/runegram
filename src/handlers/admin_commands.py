# src/handlers/admin_commands.py

from aiogram import types
from aiogram.dispatcher.filters import Command

from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service, world_service
# --- IMPORTACIÓN CORREGIDA ---
from src.utils.presenters import show_current_room

# --- Filtro de Permisos ---

async def is_admin(message: types.Message) -> bool:
    """
    Filtro de permisos. Verifica si el usuario que envía el mensaje
    tiene el rol de 'ADMINISTRADOR' en la base de datos.
    """
    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)
        if account and account.role == 'ADMINISTRADOR':
            return True

        await message.answer("⛔ No tienes permiso para usar este comando.")
        return False


# --- Comandos de Construcción del Mundo ---

@dp.message_handler(Command("crearsala"))
async def create_room_cmd(message: types.Message):
    """
    Comando de admin para crear una nueva sala.
    Uso: /crearsala [nombre de la sala]
    """
    if not await is_admin(message): return

    room_name = message.get_args()
    if not room_name:
        return await message.answer("Uso: /crearsala [nombre de la sala]")

    async with async_session_factory() as session:
        try:
            room = await world_service.create_room(session, room_name)
            await message.answer(f"✅ Sala '{room.name}' creada con éxito. ID: {room.id}")
        except Exception as e:
            await message.answer(f"❌ Error al crear la sala: {e}")


@dp.message_handler(Command("describirsala"))
async def describe_room_cmd(message: types.Message):
    """
    Comando de admin para describir la sala en la que se encuentra actualmente.
    Uso: /describirsala [descripción de la sala]
    """
    if not await is_admin(message): return

    description = message.get_args()
    if not description:
        return await message.answer("Uso: /describirsala [descripción de la sala]")

    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)
        if not account.character:
            return await message.answer("No tienes un personaje para determinar tu ubicación.")

        room_id = account.character.room_id
        await world_service.set_room_description(session, room_id, description)
        await message.answer(f"✅ Descripción de la sala actual (ID: {room_id}) actualizada.")


@dp.message_handler(Command("conectarsala"))
async def link_rooms_cmd(message: types.Message):
    """
    Comando de admin para conectar la sala actual con otra.
    Uso: /conectarsala [dirección] a [ID_sala_destino]
    """
    if not await is_admin(message): return

    args = message.get_args().split()
    if len(args) != 3 or args[1].lower() != 'a':
        return await message.answer("Uso: /conectarsala [dirección] a [ID_sala_destino]")

    direction, _, to_room_id_str = args
    try:
        to_room_id = int(to_room_id_str)
    except ValueError:
        return await message.answer("El ID de la sala de destino debe ser un número.")

    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)
        if not account.character:
            return await message.answer("No tienes un personaje para determinar tu ubicación.")

        from_room_id = account.character.room_id
        try:
            await world_service.link_rooms(session, from_room_id, direction, to_room_id)
            await message.answer(f"✅ Salida '{direction}' creada desde tu sala (ID: {from_room_id}) hacia la sala {to_room_id}.")
        except Exception as e:
            await message.answer(f"❌ Error al conectar las salas: {e}")


@dp.message_handler(Command("teleport"))
async def teleport_cmd(message: types.Message):
    """
    Comando de admin para teletransportarse a otra sala.
    Uso: /teleport [ID_sala]
    """
    if not await is_admin(message): return

    args = message.get_args()
    if not args:
        return await message.answer("Uso: /teleport [ID_sala]")

    try:
        to_room_id = int(args)
    except (ValueError, TypeError):
        return await message.answer("El ID de la sala debe ser un número.")

    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)
        if not account.character:
            return await message.answer("No tienes un personaje para teletransportar.")

        try:
            await player_service.teleport_character(session, account.character.id, to_room_id)
            await message.answer(f"🚀 Teletransportado a la sala {to_room_id}.")
            await show_current_room(message)
        except Exception as e:
            await message.answer(f"❌ Error al teletransportar: {e}")