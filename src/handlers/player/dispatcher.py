# src/handlers/player/dispatcher.py
import logging
from aiogram import types
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
from src.utils.presenters import show_current_room
from sqlalchemy.ext.asyncio import AsyncSession

# Este diccionario sigue siendo la "fuente de la verdad" de todas las instancias de comandos.
COMMAND_SETS = {
    "general": GENERAL_COMMANDS,
    "character_creation": CHARACTER_COMMANDS,
    "interaction": INTERACTION_COMMANDS,
    "movement": MOVEMENT_COMMANDS,
    "channels": CHANNEL_COMMANDS,
    "spawning": SPAWN_COMMANDS,
    "admin_movement": ADMIN_MOVEMENT_COMMANDS,
    "admin_info": INFO_COMMANDS,
}

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def main_command_dispatcher(message: types.Message):
    """
    Dispatcher principal que utiliza el command_service para determinar
    los comandos activos de un personaje de forma dinámica y actualiza su estado de actividad.
    """
    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)
        character = account.character
        input_text = message.text.strip()

        if character:
            # En cada mensaje, actualizamos la última actividad del personaje.
            # Esto también se encarga de notificar si vuelve de estar AFK.
            await online_service.update_last_seen(session, character)

        if input_text.lower().startswith('/start'):
            if character is None:
                await message.answer(
                    "¡Bienvenido a Runegram! Veo que eres nuevo por aquí. "
                    "Para empezar, necesitas crear tu personaje. Usa el comando "
                    "/crearpersonaje [nombre] para darle vida a tu aventurero."
                )
            else:
                # Al iniciar sesión, actualizamos sus comandos en Telegram.
                await command_service.update_telegram_commands(character)
                await show_current_room(message)
            return

        # Protección para usuarios sin personaje
        if not character:
            allowed_cmds = ["/crearpersonaje"]
            cmd_name_only = input_text.split()[0].lower()
            if cmd_name_only not in allowed_cmds:
                return await message.answer("Primero debes crear un personaje con /crearpersonaje.")

        if not input_text.startswith('/'):
             return await message.answer("Comando desconocido. Los comandos deben empezar con / (ej: /mirar, /norte).")

        cmd_name = message.get_command(pure=True).lower()
        args = message.get_args().split() if message.get_args() else []

        found_cmd = None
        # Obtenemos la lista de sets activos desde el servicio en cada turno.
        active_sets_names = await command_service.get_active_command_sets_for_character(character)

        for set_name in active_sets_names:
            if set_name in COMMAND_SETS:
                for cmd_instance in COMMAND_SETS[set_name]:
                    if cmd_name in cmd_instance.names:
                        found_cmd = cmd_instance
                        break
            if found_cmd:
                break

        if not found_cmd:
            return await message.answer("No conozco ese comando.")

        can_run, error_message = await permission_service.can_execute(character, found_cmd.lock)
        if not can_run:
            return await message.answer(error_message or "No puedes hacer eso.")

        try:
            await found_cmd.execute(character, session, message, args)
        except Exception as e:
            await message.answer("Ocurrió un error al ejecutar ese comando.")
            logging.exception(f"Error al ejecutar el comando /{cmd_name} para el personaje {character.name}")