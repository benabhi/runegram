# src/handlers/admin/permissions.py

from aiogram import types
from src.db import async_session_factory
from src.services import player_service


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