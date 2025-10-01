# commands/player/movement.py
"""
Módulo de Comandos de Movimiento del Jugador.

Este archivo centraliza toda la lógica relacionada con el desplazamiento del
personaje por el mundo del juego.

Utiliza una única clase genérica, `CmdMove`, que se instancia para cada una de
las direcciones posibles (norte, sur, etc.), cada una con sus propios alias.
Esto evita la duplicación de código y mantiene la lógica de movimiento en un
solo lugar.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import player_service, command_service, permission_service
from src.utils.presenters import show_current_room

class CmdMove(Command):
    """
    Comando genérico que gestiona el movimiento del jugador en una dirección.
    La dirección específica se determina por el nombre principal del comando
    (el primer elemento en la lista `names`).
    """
    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        try:
            # 1. Determinar la dirección basándose en el comando invocado.
            direction = self.names[0]

            # 2. Buscar si existe una salida válida en esa dirección.
            target_exit = next(
                (exit_obj for exit_obj in character.room.exits_from if exit_obj.name == direction),
                None
            )

            if not target_exit:
                await message.answer("No puedes ir en esa dirección.")
                return

            # 3. Comprobar permisos (Locks).
            #    Llamamos al permission_service para evaluar el lock_string de la salida.
            can_pass, error_message = await permission_service.can_execute(character, target_exit.locks)
            if not can_pass:
                # Si `can_execute` devuelve un mensaje personalizado, lo usamos.
                # Si no, usamos un mensaje genérico.
                await message.answer(error_message or "Esa salida está bloqueada.")
                return

            # 4. Mover al personaje a la nueva sala.
            await player_service.teleport_character(session, character.id, target_exit.to_room_id)

            # 5. Actualizar la lista de comandos del jugador en Telegram.
            refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
            if refreshed_character:
                await command_service.update_telegram_commands(refreshed_character)

            # 6. Mostrar al jugador la descripción de su nueva ubicación.
            await show_current_room(message)

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar moverte.")
            logging.exception(f"Fallo al ejecutar /mover ({self.names[0]}) para {character.name}")

# --- Creación del Command Set con descripciones ---
# Se crea una instancia de `CmdMove` para cada dirección, asignando sus alias
# y una descripción clara para la lista de comandos de Telegram.
MOVEMENT_COMMANDS = [
    CmdMove(names=["norte", "n"], description="Moverse hacia el norte."),
    CmdMove(names=["sur", "s"], description="Moverse hacia el sur."),
    CmdMove(names=["este", "e"], description="Moverse hacia el este."),
    CmdMove(names=["oeste", "o"], description="Moverse hacia el oeste."),
    CmdMove(names=["arriba", "ar"], description="Moverse hacia arriba."),
    CmdMove(names=["abajo", "ab"], description="Moverse hacia abajo."),
    CmdMove(names=["noreste", "ne"], description="Moverse hacia el noreste."),
    CmdMove(names=["noroeste", "no"], description="Moverse hacia el noroeste."),
    CmdMove(names=["sureste", "se"], description="Moverse hacia el sureste."),
    CmdMove(names=["suroeste", "so"], description="Moverse hacia el suroeste."),
]