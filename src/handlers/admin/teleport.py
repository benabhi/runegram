# src/handlers/admin/teleport.py

from aiogram import types
from aiogram.dispatcher.filters import Command

from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service
from src.utils.presenters import show_current_room
from src.handlers.admin.permissions import is_admin


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