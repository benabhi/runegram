# src/handlers/player/dispatcher.py
"""
Módulo del Dispatcher Principal de Comandos.

Este archivo contiene el manejador (`handler`) más importante de la aplicación.
La función `main_command_dispatcher` está registrada para interceptar **todos**
los mensajes de texto enviados por los jugadores.

Actúa como el "cerebro" del juego, orquestando el siguiente flujo para cada mensaje:
1. Obtiene el contexto del jugador (Cuenta, Personaje) desde la base de datos.
2. Actualiza el estado de actividad del jugador (online/AFK).
3. Maneja casos especiales como el comando `/start`.
4. Utiliza el `command_service` para determinar dinámicamente qué `CommandSets`
   están activos para el jugador en ese preciso momento.
5. Busca el comando invocado dentro de los sets activos.
6. Verifica los permisos (`permission_service`).
7. Ejecuta el método `.execute()` del comando encontrado.
"""

import logging
from aiogram import types
from aiogram.types import InputFile # <-- Importación añadida
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service, permission_service, online_service, command_service
from src.utils.inline_keyboards import create_character_creation_keyboard

# Importaciones de CommandSets de Jugador
from commands.player.general import GENERAL_COMMANDS
from commands.player.character import CHARACTER_COMMANDS
from commands.player.interaction import INTERACTION_COMMANDS
from commands.player.movement import MOVEMENT_COMMANDS
from commands.player.channels import CHANNEL_COMMANDS
from commands.player.dynamic_channels import DYNAMIC_CHANNEL_COMMANDS
from commands.player.settings import SETTINGS_COMMANDS
from commands.player.listing import LISTING_COMMANDS

# Importaciones de CommandSets de Administrador
from commands.admin.building import SPAWN_COMMANDS
from commands.admin.movement import ADMIN_MOVEMENT_COMMANDS
from commands.admin.info import INFO_COMMANDS
from commands.admin.diagnostics import DIAGNOSTICS_COMMANDS
from commands.admin.management import MANAGEMENT_COMMANDS

from src.utils.presenters import show_current_room

# El diccionario `COMMAND_SETS` es el catálogo maestro que contiene una instancia
# de cada comando disponible en el juego, agrupados por funcionalidad.
COMMAND_SETS = {
    # Comandos de Jugador
    "general": GENERAL_COMMANDS,
    "character_creation": CHARACTER_COMMANDS,
    "interaction": INTERACTION_COMMANDS,
    "movement": MOVEMENT_COMMANDS,
    "channels": CHANNEL_COMMANDS,
    "dynamic_channels": DYNAMIC_CHANNEL_COMMANDS,
    "settings": SETTINGS_COMMANDS,
    "listing": LISTING_COMMANDS,
    # Comandos de Administrador
    "spawning": SPAWN_COMMANDS,
    "admin_movement": ADMIN_MOVEMENT_COMMANDS,
    "admin_info": INFO_COMMANDS,
    "diagnostics": DIAGNOSTICS_COMMANDS,
    "management": MANAGEMENT_COMMANDS,
}

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def main_command_dispatcher(message: types.Message):
    """
    Manejador principal que intercepta todos los mensajes de texto y los
    enruta al comando correspondiente.
    """
    async with async_session_factory() as session:
        try:
            # 1. Obtener el contexto del jugador.
            account = await player_service.get_or_create_account(session, message.from_user.id)
            if not account:
                await message.answer("Error crítico al acceder a tu cuenta.")
                return
            character = account.character
            input_text = message.text.strip()

            # 2. Actualizar estado de actividad (online/AFK).
            if character:
                await online_service.update_last_seen(session, character)

            # 3. Manejo especial para el comando /start.
            if input_text.lower().startswith('/start'):
                if character is None:

                    photo_path = "/app/assets/images/runegram_cover.png"

                    try:
                        # Se intenta enviar la foto desde la ruta dentro del contenedor.
                        await message.bot.send_photo(
                            chat_id=message.chat.id,
                            photo=InputFile(photo_path)
                        )
                    except FileNotFoundError:
                        # Si la imagen no se encuentra, se registra una advertencia
                        # pero el bot continúa funcionando, enviando solo el texto.
                        logging.warning(f"No se encontró la imagen de portada en la ruta: {photo_path}")
                    except Exception:
                        # Captura otros posibles errores de la API de Telegram.
                        logging.exception("Error al enviar la foto de portada.")

                    # El mensaje de texto se envía después de la imagen con botón inline.
                    keyboard = create_character_creation_keyboard()
                    await message.answer(
                        "¡Bienvenido a Runegram! Veo que eres nuevo por aquí.\n"
                        "Para empezar, necesitas crear tu personaje. Usa el comando:\n"
                        "/crearpersonaje [nombre]\n\n"
                        "O toca el botón de abajo:",
                        reply_markup=keyboard
                    )
                else:
                    await command_service.update_telegram_commands(character)
                    await show_current_room(message)
                return

            # 4. Validar que el jugador tenga un personaje para la mayoría de los comandos.
            # Esta lógica se ha movido dentro del parseo para simplificar.

            # 5. Parsear el comando y sus argumentos.
            if not input_text.startswith('/'):
                await message.answer("Comando desconocido. Los comandos deben empezar con / (ej: /mirar, /norte).")
                return

            cmd_name = message.get_command(pure=True).lower()
            args = message.get_args().split() if message.get_args() else []

            # 6. Obtener la lista dinámica de CommandSets activos.
            active_sets_names = await command_service.get_active_command_sets_for_character(character)

            # 7. Buscar y ejecutar el comando.
            found_cmd = None
            for set_name in active_sets_names:
                for cmd_instance in COMMAND_SETS.get(set_name, []):
                    if cmd_name in cmd_instance.names:
                        found_cmd = cmd_instance
                        break
                if found_cmd:
                    break

            if not found_cmd:
                # Si el jugador no tiene personaje y el comando no es de creación, damos un mensaje específico.
                if not character and cmd_name != "crearpersonaje":
                     keyboard = create_character_creation_keyboard()
                     await message.answer(
                         "Primero debes crear un personaje con /crearpersonaje [nombre].\n\n"
                         "O toca el botón de abajo:",
                         reply_markup=keyboard
                     )
                else:
                    await message.answer("No conozco ese comando.")
                return

            can_run, error_message = await permission_service.can_execute(character, found_cmd.lock)
            if not can_run:
                await message.answer(error_message or "No puedes hacer eso.")
                return

            await found_cmd.execute(character, session, message, args)

        except Exception:
            # Captura final para cualquier error no manejado en las capas inferiores.
            await message.answer("Ocurrió un error inesperado al procesar tu comando.")
            logging.exception(f"Error crítico no manejado en el dispatcher principal para el usuario {message.from_user.id}")