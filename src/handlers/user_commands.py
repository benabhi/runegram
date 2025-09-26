# src/handlers/user_commands.py

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import Command

from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service
# --- IMPORTACIÓN CORREGIDA ---
from src.utils.presenters import show_current_room


# --- Handlers de Comandos de Jugador ---

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    """
    Este manejador se activa con el comando /start.
    Registra al usuario si no existe, carga su personaje y le muestra la sala actual.
    """
    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)

        if account.character is None:
            # Si el jugador no tiene personaje, le guiamos para que lo cree.
            await message.answer(
                "¡Bienvenido a Runegram! Veo que eres nuevo por aquí. "
                "Para empezar, necesitas crear tu personaje. Usa el comando "
                "/crearpersonaje [nombre] para darle vida a tu aventurero."
            )
        else:
            # Si ya tiene un personaje, simplemente le mostramos dónde está.
            await show_current_room(message)


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


@dp.message_handler(Command("mirar"))
async def look_handler(message: types.Message):
    """
    Manejador para el comando /mirar. Simplemente muestra la sala actual.
    """
    await show_current_room(message)


# --- Handler de Texto (Movimiento y Futuro Parser) ---

@dp.message_handler()
async def text_handler(message: types.Message):
    """
    Este handler captura cualquier mensaje de texto que no sea un comando.
    Actualmente, solo gestiona el movimiento.
    """
    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)
        if not account.character:
            return await message.answer("Primero debes crear un personaje con /crearpersonaje.")

        command = message.text.lower().strip()
        current_room = account.character.room

        if command in current_room.exits:
            to_room_id = current_room.exits[command]
            await player_service.teleport_character(session, account.character.id, to_room_id)
            await show_current_room(message)
        else:
            await message.answer("No entiendo ese comando.")