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
from src.services import player_service
from src.utils.presenters import show_current_room

class CmdTeleport(Command):
    """
    Comando para teletransportar al administrador a cualquier sala del juego
    especificando su ID numérico.
    """
    names = ["teleport", "tp"]
    lock = "rol(ADMINISTRADOR)"
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
            # 2. Llamar al servicio que contiene la lógica de negocio.
            await player_service.teleport_character(session, character.id, to_room_id)

            # 3. Notificar al administrador del éxito y mostrar la nueva ubicación.
            await message.answer(f"🚀 Teletransportado a la sala {to_room_id}.")
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