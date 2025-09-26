# src/handlers/player/movement.py

from aiogram import types

from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service, permission_service
from src.commands.general import GENERAL_COMMANDS
from src.commands.interaction import INTERACTION_COMMANDS # <-- Importa el nuevo set


# --- El Router de Command Sets ---
COMMAND_SETS = {
    "general": GENERAL_COMMANDS,
    "interaction": INTERACTION_COMMANDS, # <-- Añádelo al diccionario
}


@dp.message_handler()
async def text_handler(message: types.Message):
    """
    Este handler captura cualquier mensaje de texto que no sea un comando con '/'.
    Actúa como el parser principal del juego.
    """
    if message.text.startswith('/'):
        return

    async with async_session_factory() as session:
        account = await player_service.get_or_create_account(session, message.from_user.id)
        if not account.character:
            return await message.answer("Primero debes crear un personaje con /crearpersonaje.")

        character = account.character
        input_text = message.text.lower().strip()
        parts = input_text.split()
        cmd_name = parts[0]
        args = parts[1:]

        # --- Lógica de Movimiento (Prioridad 1) ---
        current_room = character.room
        if cmd_name in current_room.exits:
            to_room_id = current_room.exits[cmd_name]
            await player_service.teleport_character(session, character.id, to_room_id)
            return

        # --- Lógica del Parser de Comandos (Prioridad 2) ---
        found_cmd = None
        # Añadimos "interaction" a la lista de sets a buscar
        # En el futuro, esto vendrá del `character.command_sets`
        active_sets = ["general", "interaction"]
        for set_name in active_sets:
            if set_name in COMMAND_SETS:
                for cmd_instance in COMMAND_SETS[set_name]:
                    if cmd_name in cmd_instance.names:
                        found_cmd = cmd_instance
                        break
            if found_cmd:
                break

        if not found_cmd:
            return await message.answer("No entiendo ese comando.")

        # Verificar permisos y ejecutar
        can_run, error_message = await permission_service.can_execute(character, found_cmd.lock)
        if not can_run:
            return await message.answer(error_message or "No puedes hacer eso.")

        try:
            await found_cmd.execute(character, session, message, args)
        except Exception as e:
            await message.answer("Ocurrió un error al ejecutar ese comando.")
            print(f"Error ejecutando {cmd_name}: {e}")