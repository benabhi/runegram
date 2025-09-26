# src/handlers/player/character.py

from aiogram import types
from aiogram.dispatcher.filters import Command

from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service


@dp.message_handler(Command("crearpersonaje"))
async def create_character_handler(message: types.Message):
    """
    Manejador para el comando /crearpersonaje [nombre].
    """
    async with async_session_factory() as session:
        telegram_id = message.from_user.id

        character_name = message.get_args()
        if not character_name or len(character_name) > 50:
            await message.answer("Por favor, proporciona un nombre válido (máx 50 caracteres). Uso: /crearpersonaje [nombre]")
            return

        try:
            character = await player_service.create_character(
                session=session,
                telegram_id=telegram_id,
                character_name=character_name
            )
            await message.answer(
                f"¡Tu personaje, {character.name}, ha sido creado con éxito!\n"
                "Ahora estás listo para explorar el mundo de Runegram. ¡Envía /start para comenzar!"
            )
        except ValueError as e:
            await message.answer(f"No se pudo crear el personaje: {e}")
        except Exception as e:
            await message.answer(f"Ocurrió un error inesperado al crear tu personaje.")
            print(f"Error en create_character_handler: {e}")