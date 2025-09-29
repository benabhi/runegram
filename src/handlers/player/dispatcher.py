# src/handlers/player/dispatcher.py
from aiogram import types
from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service, permission_service
from commands.player.general import GENERAL_COMMANDS
from commands.player.character import CHARACTER_COMMANDS
from commands.player.interaction import INTERACTION_COMMANDS
from commands.admin.building import BUILDING_COMMANDS
from commands.admin.movement import ADMIN_MOVEMENT_COMMANDS
from src.utils.presenters import show_current_room
from sqlalchemy.ext.asyncio import AsyncSession

# --- El Router de Command Sets ---
COMMAND_SETS = {
    "general": GENERAL_COMMANDS,
    "character_creation": CHARACTER_COMMANDS,
    "interaction": INTERACTION_COMMANDS,
    "building": BUILDING_COMMANDS,
    "admin_movement": ADMIN_MOVEMENT_COMMANDS,
}

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def main_command_dispatcher(message: types.Message):
    """
    Este es el dispatcher principal. Captura todo el texto, lo interpreta
    y lo dirige a la lógica correspondiente (movimiento o comando).
    """
    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)
        character = account.character
        input_text = message.text.strip() # Usamos strip() al principio

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
            # Extraemos el comando para compararlo
            cmd_name_only = input_text.split()[0].lower()
            if cmd_name_only not in allowed_cmds:
                return await message.answer("Primero debes crear un personaje con /crearpersonaje.")

        # --- Lógica de Movimiento (Prioridad 1) ---
        if not input_text.startswith('/'):
            command_as_exit = next(
                (exit_obj for exit_obj in character.room.exits_from if exit_obj.name == input_text.lower()),
                None
            )
            if command_as_exit:
                await player_service.teleport_character(session, character.id, command_as_exit.to_room_id)
                await show_current_room(message)
                return

        # --- Lógica del Parser de Comandos (Prioridad 2) ---
        if not input_text.startswith('/'):
             return await message.answer("No entiendo ese comando. Los comandos empiezan con / (ej: /mirar) o son salidas (ej: norte).")

        cmd_name = message.get_command(pure=True).lower()
        args = message.get_args().split() if message.get_args() else []

        found_cmd = None
        active_sets_names = ["general", "interaction"]
        if not character:
            active_sets_names.append("character_creation")
        if account.role == "ADMINISTRADOR":
            active_sets_names.extend(["building", "admin_movement"])

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
            print(f"Error ejecutando /{cmd_name}: {e}")