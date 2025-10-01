# commands/player/interaction.py
"""
Módulo de Comandos de Interacción con Objetos.

Este archivo contiene los comandos que permiten al jugador manipular directamente
los objetos (`Items`) en el mundo del juego.

Incluye acciones fundamentales como coger objetos del entorno y dejar
objetos del inventario.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import item_service, command_service, player_service

class CmdGet(Command):
    """
    Comando para que un jugador recoja un objeto del suelo en su sala actual
    y lo añada a su inventario.
    """
    names = ["coger", "g"]
    lock = ""
    description = "Recoge un objeto del suelo."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            if not args:
                await message.answer("¿Qué quieres coger?")
                return

            item_name_to_get = " ".join(args).lower()
            item_to_get = None

            # Buscamos el objeto en la lista de items de la sala actual.
            for item in character.room.items:
                if item_name_to_get in item.get_name().lower():
                    item_to_get = item
                    break

            if not item_to_get:
                await message.answer("No ves eso por aquí.")
                return

            # Llamamos al servicio para actualizar la ubicación del objeto en la BD.
            await item_service.move_item_to_character(session, item_to_get.id, character.id)

            # Si el objeto que cogimos otorga un CommandSet, debemos actualizar la
            # lista de comandos del jugador en Telegram.
            if item_to_get.prototype.get("grants_command_sets"):
                refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
                await command_service.update_telegram_commands(refreshed_character)

            await message.answer(f"Has cogido: {item_to_get.get_name()}")
        except Exception:
            await message.answer("❌ Ocurrió un error al intentar coger el objeto.")
            logging.exception(f"Fallo al ejecutar /coger para {character.name}")


class CmdDrop(Command):
    """
    Comando para que un jugador deje un objeto de su inventario en el suelo
    de su sala actual.
    """
    names = ["dejar", "d"]
    lock = ""
    description = "Deja un objeto de tu inventario en el suelo."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            if not args:
                await message.answer("¿Qué quieres dejar?")
                return

            item_name_to_drop = " ".join(args).lower()
            item_to_drop = None

            # Buscamos el objeto en el inventario del personaje.
            for item in character.items:
                if item_name_to_drop in item.get_name().lower():
                    item_to_drop = item
                    break

            if not item_to_drop:
                await message.answer("No llevas eso.")
                return

            # Llamamos al servicio para actualizar la ubicación del objeto en la BD.
            await item_service.move_item_to_room(session, item_to_drop.id, character.room_id)

            # Si el objeto que dejamos otorgaba un CommandSet, debemos actualizar la
            # lista de comandos del jugador en Telegram.
            if item_to_drop.prototype.get("grants_command_sets"):
                refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
                await command_service.update_telegram_commands(refreshed_character)

            await message.answer(f"Has dejado: {item_to_drop.get_name()}")
        except Exception:
            await message.answer("❌ Ocurrió un error al intentar dejar el objeto.")
            logging.exception(f"Fallo al ejecutar /dejar para {character.name}")


# Exportamos la lista de comandos de este módulo.
INTERACTION_COMMANDS = [
    CmdGet(),
    CmdDrop(),
]