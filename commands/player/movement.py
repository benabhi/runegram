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
from src.services import player_service, command_service, permission_service, broadcaster_service
from src.utils.presenters import show_current_room

# Mapeo de direcciones opuestas para los mensajes de llegada
OPPOSITE_DIRECTIONS = {
    "norte": "sur",
    "sur": "norte",
    "este": "oeste",
    "oeste": "este",
    "arriba": "abajo",
    "abajo": "arriba",
    "noreste": "suroeste",
    "suroeste": "noreste",
    "noroeste": "sureste",
    "sureste": "noroeste",
}

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

            # 3. Comprobar permisos (Locks) con access type "traverse".
            #    Llamamos al permission_service para evaluar el lock de la salida.
            can_pass, error_message = await permission_service.can_execute(
                character,
                target_exit.locks,
                access_type="traverse"
            )
            if not can_pass:
                # Si `can_execute` devuelve un mensaje personalizado, lo usamos.
                # Si no, usamos un mensaje genérico.
                await message.answer(error_message or "Esa salida está bloqueada.")
                return

            # 4. Guardar la sala de origen para notificar la salida.
            old_room_id = character.room_id

            # 5. Notificar a la sala de origen que el personaje se fue.
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=old_room_id,
                message_text=f"<i>{character.name} se ha ido hacia el {direction}.</i>",
                exclude_character_id=character.id
            )

            # 6. Mover al personaje a la nueva sala.
            await player_service.teleport_character(session, character.id, target_exit.to_room_id)

            # 7. Notificar a la sala de destino que el personaje llegó.
            #    Usamos la dirección opuesta para el mensaje de llegada.
            opposite_direction = OPPOSITE_DIRECTIONS.get(direction, "alguna parte")
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=target_exit.to_room_id,
                message_text=f"<i>{character.name} ha llegado desde el {opposite_direction}.</i>",
                exclude_character_id=character.id
            )

            # 8. Actualizar la lista de comandos del jugador en Telegram.
            refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
            if refreshed_character:
                await command_service.update_telegram_commands(refreshed_character)

            # 9. Mostrar al jugador la descripción de su nueva ubicación.
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