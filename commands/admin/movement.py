# commands/admin/movement.py
"""
Módulo de Comandos Administrativos para el Movimiento.

Este archivo contiene comandos que otorgan a los administradores capacidades
de movimiento especiales, que no están sujetas a las reglas normales del juego
(como las salidas definidas en una sala).

Son herramientas esenciales para la construcción, supervisión y depuración del mundo.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import player_service, command_service, narrative_service, broadcaster_service
from src.utils.presenters import show_current_room

class CmdTeleport(Command):
    """
    Comando para teletransportar al administrador a cualquier sala del juego
    especificando su ID numérico.
    """
    names = ["teleport", "tp"]
    lock = "rol(ADMIN)"  # Solo usuarios con rol ADMIN o superior pueden usarlo.
    description = "Teletranspórtate a cualquier sala usando su ID."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        # 1. Validar la entrada del usuario.
        if not args:
            await message.answer("Uso: /teleport [ID_sala]")
            return

        try:
            # Intentamos convertir el primer argumento a un número entero.
            to_room_id = int(args[0])
        except (ValueError, IndexError):
            # Falla si no hay argumentos o si el argumento no es un número.
            await message.answer("El ID de la sala debe ser un número válido.")
            return

        try:
            # 2. Notificar a la sala de origen sobre la salida del admin (broadcast)
            origin_room_id = character.room_id
            departure_message = narrative_service.get_random_narrative(
                "teleport_departure",
                character_name=character.name
            )
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=origin_room_id,
                message_text=departure_message,
                exclude_character_id=character.id  # El admin no ve su propia salida
            )

            # 3. Llamar al servicio que contiene la lógica de negocio.
            await player_service.teleport_character(session, character.id, to_room_id)

            # 4. Notificar a la sala de destino sobre la llegada del admin (broadcast)
            arrival_message = narrative_service.get_random_narrative(
                "teleport_arrival",
                character_name=character.name
            )
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=to_room_id,
                message_text=arrival_message,
                exclude_character_id=character.id  # El admin no ve su propia llegada
            )

            # 5. Notificar al administrador del éxito.
            await message.answer(f"🚀 Teletransportado a la sala {to_room_id}.")

            # 6. Actualizar los comandos de Telegram, ya que la nueva sala puede otorgar sets.
            refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
            if refreshed_character:
                 await command_service.update_telegram_commands(refreshed_character)

            # 7. Mostrar la nueva ubicación.
            await show_current_room(message)

        except Exception as e:
            # Capturamos cualquier error que pueda ocurrir durante el teletransporte,
            # como un ID de sala que no existe (manejado por `player_service`).
            await message.answer(f"❌ Error al teletransportar: {e}")
            logging.warning(f"Fallo al ejecutar /teleport a la sala {args[0]}: {e}")

# Exportamos la lista de comandos de este módulo.
ADMIN_MOVEMENT_COMMANDS = [
    CmdTeleport(),
]