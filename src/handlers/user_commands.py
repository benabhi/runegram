from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from src.bot.dispatcher import dp

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    """
    Este manejador se activa con el comando /start.
    """
    await message.answer("¡Hola, mundo! Runegram está en línea.")