# src/handlers/player/dispatcher.py
import logging
from aiogram import types
from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service, permission_service, online_service
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

# --- El Router de Command Sets (Actualizado) ---
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
    Dispatcher principal que ahora también actualiza la actividad del jugador.
    """
    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)
        character = account.character
        input_text = message.text.strip()

        # Si el personaje existe, actualizamos su última actividad en cada mensaje.
        if character:
            await online_service.update_last_seen(character.id)

        # --- Manejo especial para /start ---
        if input_text.lower().startswith('/start'):
            if character is None:
                await message.answer(
                    "¡Bienvenido a Runegram! Veo que eres nuevo por aquí. "
                    "Para empezar, necesitas crear tu personaje. Usa el comando "
                    "/crearpersonaje [nombre] para darle vida a tu aventurero."
                )
            else:
                await show_current_room(message)
            return

        # --- Protección para usuarios sin personaje ---
        if not character:
            allowed_cmds = ["/crearpersonaje"]
            cmd_name_only = input_text.split()[0].lower()
            if cmd_name_only not in allowed_cmds:
                return await message.answer("Primero debes crear un personaje con /crearpersonaje.")

        # --- Lógica del Parser de Comandos ---
        if not input_text.startswith('/'):
             return await message.answer("Comando desconocido. Los comandos deben empezar con / (ej: /mirar, /norte).")

        cmd_name = message.get_command(pure=True).lower()
        args = message.get_args().split() if message.get_args() else []

        found_cmd = None
        # Añadimos "channels" a los sets de comandos por defecto para todos los jugadores.
        active_sets_names = ["general", "interaction", "movement", "channels"]
        if not character:
            active_sets_names.append("character_creation")

        if account.role == "ADMINISTRADOR":
            active_sets_names.extend(["spawning", "admin_movement", "admin_info"])

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