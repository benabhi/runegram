# src/handlers/player/dispatcher.py
# (No se requieren cambios en este archivo, la refactorización es interna al CommandSet `channels`)

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service, permission_service, online_service, command_service
from commands.player.general import GENERAL_COMMANDS
from commands.player.character import CHARACTER_COMMANDS
from commands.player.interaction import INTERACTION_COMMANDS
from commands.player.movement import MOVEMENT_COMMANDS
from commands.player.channels import CHANNEL_COMMANDS
from commands.admin.building import SPAWN_COMMANDS
from commands.admin.movement import ADMIN_MOVEMENT_COMMANDS
from commands.admin.info import INFO_COMMANDS
from commands.admin.diagnostics import DIAGNOSTICS_COMMANDS
from src.utils.presenters import show_current_room

COMMAND_SETS = {
    "general": GENERAL_COMMANDS,
    "character_creation": CHARACTER_COMMANDS,
    "interaction": INTERACTION_COMMANDS,
    "movement": MOVEMENT_COMMANDS,
    "channels": CHANNEL_COMMANDS,
    "spawning": SPAWN_COMMANDS,
    "admin_movement": ADMIN_MOVEMENT_COMMANDS,
    "admin_info": INFO_COMMANDS,
    "diagnostics": DIAGNOSTICS_COMMANDS,
}

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def main_command_dispatcher(message: types.Message):
    async with async_session_factory() as session:
        try:
            account = await player_service.get_or_create_account(session, message.from_user.id)
            if not account:
                await message.answer("Error crítico al acceder a tu cuenta.")
                return
            character = account.character
            input_text = message.text.strip()

            if character:
                await online_service.update_last_seen(session, character)

            if input_text.lower().startswith('/start'):
                if character is None:
                    await message.answer(
                        "¡Bienvenido a Runegram! Veo que eres nuevo por aquí.\n"
                        "Para empezar, necesitas crear tu personaje. Usa el comando:\n"
                        "/crearpersonaje [nombre]"
                    )
                else:
                    await command_service.update_telegram_commands(character)
                    await show_current_room(message)
                return

            if not character:
                if not input_text.lower().startswith('/crearpersonaje'):
                    await message.answer("Primero debes crear un personaje con /crearpersonaje [nombre].")

            if not input_text.startswith('/'):
                await message.answer("Comando desconocido. Los comandos deben empezar con / (ej: /mirar, /norte).")
                return

            cmd_name = message.get_command(pure=True).lower()
            args = message.get_args().split() if message.get_args() else []

            active_sets_names = await command_service.get_active_command_sets_for_character(character)

            found_cmd = None
            for set_name in active_sets_names:
                for cmd_instance in COMMAND_SETS.get(set_name, []):
                    if cmd_name in cmd_instance.names:
                        found_cmd = cmd_instance
                        break
                if found_cmd:
                    break

            if not found_cmd:
                await message.answer("No conozco ese comando.")
                return

            if not character and found_cmd.lock:
                await message.answer("Primero debes crear un personaje con /crearpersonaje [nombre].")
                return

            can_run, error_message = await permission_service.can_execute(character, found_cmd.lock)
            if not can_run:
                await message.answer(error_message or "No puedes hacer eso.")
                return

            await found_cmd.execute(character, session, message, args)

        except Exception:
            await message.answer("Ocurrió un error inesperado al procesar tu comando.")
            logging.exception(f"Error crítico no manejado en el dispatcher principal para el usuario {message.from_user.id}")