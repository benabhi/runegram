# src/handlers/admin/create.py

from aiogram import types
from aiogram.dispatcher.filters import Command

from src.bot.dispatcher import dp
from src.db import async_session_factory
# Añadimos player_service y item_service
from src.services import player_service, world_service, item_service
from src.handlers.admin.permissions import is_admin


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


# --- NUEVO HANDLER AÑADIDO ---
@dp.message_handler(Command("crearitem"))
async def create_item_cmd(message: types.Message):
    """
    Comando de admin para crear un objeto en la sala actual.
    Uso: /crearitem [key] | [nombre] | [descripción]
    """
    if not await is_admin(message): return

    args_text = message.get_args()
    if not args_text or args_text.count('|') != 2:
        return await message.answer("Uso: /crearitem [key] | [nombre] | [descripción]")

    try:
        key, name, description = [arg.strip() for arg in args_text.split('|')]
    except ValueError:
        return await message.answer("Error en el formato. Asegúrate de usar los tres argumentos separados por '|'.")

    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)
        if not account.character:
            return await message.answer("No tienes un personaje para determinar tu ubicación.")

        room_id = account.character.room_id
        try:
            item = await item_service.create_item_in_room(session, room_id, key, name, description)
            await message.answer(f"✅ Objeto '{item.name}' creado en la sala actual. ID: {item.id}")
        except Exception as e:
            await message.answer(f"❌ Error al crear el objeto: {e}")