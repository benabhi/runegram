# src/handlers/player/system.py

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import Command

from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service
from src.utils.presenters import show_current_room


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    """
    Este manejador se activa con el comando /start.
    Registra al usuario si no existe, carga su personaje y le muestra la sala actual.
    """
    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)

        if account.character is None:
            await message.answer(
                "¡Bienvenido a Runegram! Veo que eres nuevo por aquí. "
                "Para empezar, necesitas crear tu personaje. Usa el comando "
                "/crearpersonaje [nombre] para darle vida a tu aventurero."
            )
        else:
            await show_current_room(message)


@dp.message_handler(Command("ayuda"))
async def help_cmd(message: types.Message):
    """
    Muestra una lista de comandos básicos.
    """
    help_text = (
        "<b>Comandos Básicos de Runegram</b>\n"
        "---------------------------------\n"
        "<b>mirar</b> - Muestra la descripción de tu entorno.\n"
        "<b>inventario</b> - Muestra los objetos que llevas.\n"
        "<b>decir [mensaje]</b> - Hablas a la gente en tu misma sala.\n"
        "<b>coger [objeto]</b> - Recoges un objeto del suelo.\n"
        "<b>dejar [objeto]</b> - Dejas un objeto que llevas.\n\n"
        "Para moverte, simplemente escribe la dirección (ej: <b>norte</b>)."
    )
    await message.answer(f"<pre>{help_text}</pre>", parse_mode="HTML")