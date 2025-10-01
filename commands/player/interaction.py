# commands/player/interaction.py
"""
Módulo de Comandos de Interacción con Objetos.

Este archivo contiene los comandos que permiten al jugador manipular directamente
los objetos (`Items`) en el mundo del juego, incluyendo la interacción con
objetos que funcionan como contenedores.
"""

import logging
import re
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from collections import Counter

from commands.command import Command
from src.models.character import Character
from src.services import item_service, command_service, player_service, permission_service

# --- Funciones de Ayuda (Compartidas en este módulo) ---

def find_item_in_list(item_name: str, item_list: list):
    """Busca un objeto en una lista por su nombre o keywords."""
    for item in item_list:
        if item_name in item.get_keywords() or item_name == item.get_name().lower():
            return item
    return None

def parse_interaction_args(args: list[str]) -> tuple[str | None, str | None]:
    """
    Parsea argumentos complejos como "espada en mochila" o "pocion de cofre".
    Devuelve (nombre_objeto, nombre_contenedor).
    """
    arg_string = " ".join(args).lower()
    match = re.search(r'\s(en|dentro de|de|desde)\s', arg_string)
    if match:
        parts = re.split(r'\s(?:en|dentro de|de|desde)\s', arg_string, 1)
        return parts[0].strip(), parts[1].strip()
    return arg_string, None

# --- Comandos de Interacción ---

class CmdGet(Command):
    """
    Comando para coger un objeto, ya sea del suelo o de un contenedor.
    Delega a `CmdTake` si la sintaxis incluye un contenedor.
    """
    names = ["coger", "g"]
    description = "Recoge un objeto. Uso: /coger <objeto> [de <contenedor>]"
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            if not args:
                await message.answer("¿Qué quieres coger?")
                return

            item_name_to_get, container_name = parse_interaction_args(args)

            # Si se especifica un contenedor, esta acción es en realidad "sacar".
            # Delegamos la ejecución a una nueva instancia de `CmdTake`.
            if container_name:
                await CmdTake().execute(character, session, message, args)
                return

            # Lógica para coger un objeto del suelo.
            item_to_get = find_item_in_list(item_name_to_get, character.room.items)
            if not item_to_get:
                await message.answer("No ves eso por aquí.")
                return

            lock_string = item_to_get.prototype.get("locks", "")
            can_pass, error_message = await permission_service.can_execute(character, lock_string)
            if not can_pass:
                await message.answer(error_message or "No puedes coger eso.")
                return

            await item_service.move_item_to_character(session, item_to_get.id, character.id)

            if item_to_get.prototype.get("grants_command_sets"):
                refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
                await command_service.update_telegram_commands(refreshed_character)

            await message.answer(f"Has cogido: {item_to_get.get_name()}")
        except Exception:
            await message.answer("❌ Ocurrió un error al intentar coger el objeto.")
            logging.exception(f"Fallo al ejecutar /coger para {character.name}")

class CmdDrop(Command):
    """Comando para dejar un objeto del inventario en el suelo."""
    names = ["dejar", "d"]
    description = "Deja un objeto en el suelo. Uso: /dejar <objeto>"
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            if not args:
                await message.answer("¿Qué quieres dejar?")
                return

            item_to_drop_name = " ".join(args).lower()
            item_to_drop = find_item_in_list(item_to_drop_name, character.items)

            if not item_to_drop:
                await message.answer("No llevas eso.")
                return

            await item_service.move_item_to_room(session, item_to_drop.id, character.room_id)

            if item_to_drop.prototype.get("grants_command_sets"):
                refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
                await command_service.update_telegram_commands(refreshed_character)

            await message.answer(f"Has dejado: {item_to_drop.get_name()}")
        except Exception:
            await message.answer("❌ Ocurrió un error al intentar dejar el objeto.")
            logging.exception(f"Fallo al ejecutar /dejar para {character.name}")

class CmdPut(Command):
    """Comando para meter un objeto en un contenedor."""
    names = ["meter", "guardar"]
    description = "Guarda un objeto en un contenedor. Uso: /meter <objeto> en <contenedor>"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            item_name, container_name = parse_interaction_args(args)
            if not item_name or not container_name:
                await message.answer("Uso: /meter <objeto> en <contenedor>")
                return

            container = find_item_in_list(container_name, character.items) or \
                        find_item_in_list(container_name, character.room.items)
            if not container:
                await message.answer(f"No ves ningún '{container_name}' por aquí.")
                return
            if not container.prototype.get("is_container"):
                await message.answer(f"{container.get_name().capitalize()} no es un contenedor.")
                return

            lock_string = container.prototype.get("locks", "")
            can_pass, _ = await permission_service.can_execute(character, lock_string)
            if not can_pass:
                await message.answer(f"No puedes meter nada en {container.get_name()}.")
                return

            capacity = container.prototype.get("capacity", 999)
            await session.refresh(container, attribute_names=['contained_items'])
            if len(container.contained_items) >= capacity:
                await message.answer(f"{container.get_name().capitalize()} está lleno.")
                return

            item_to_store = find_item_in_list(item_name, character.items) or \
                            find_item_in_list(item_name, character.room.items)
            if not item_to_store:
                await message.answer(f"No tienes ni ves ningún '{item_name}'.")
                return
            if item_to_store.id == container.id:
                await message.answer("No puedes meter un objeto dentro de sí mismo.")
                return

            await item_service.move_item_to_container(session, item_to_store.id, container.id)
            await message.answer(f"Guardas {item_to_store.get_name()} en {container.get_name()}.")

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar guardar el objeto.")
            logging.exception(f"Fallo al ejecutar /meter para {character.name}")

class CmdTake(Command):
    """Comando para sacar un objeto de un contenedor."""
    names = ["sacar"]
    description = "Saca un objeto de un contenedor. Uso: /sacar <objeto> de <contenedor>"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            item_name, container_name = parse_interaction_args(args)
            if not item_name or not container_name:
                await message.answer("Uso: /sacar <objeto> de <contenedor>")
                return

            container = find_item_in_list(container_name, character.items) or \
                        find_item_in_list(container_name, character.room.items)
            if not container:
                await message.answer(f"No ves ningún '{container_name}' por aquí.")
                return

            lock_string = container.prototype.get("locks", "")
            can_pass, _ = await permission_service.can_execute(character, lock_string)
            if not can_pass:
                await message.answer(f"No puedes sacar nada de {container.get_name()}.")
                return

            await session.refresh(container, attribute_names=['contained_items'])
            item_to_take = find_item_in_list(item_name, container.contained_items)
            if not item_to_take:
                await message.answer(f"No ves ningún '{item_name}' en {container.get_name()}.")
                return

            await item_service.move_item_to_character(session, item_to_take.id, character.id)
            await message.answer(f"Sacas {item_to_take.get_name()} de {container.get_name()}.")

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar sacar el objeto.")
            logging.exception(f"Fallo al ejecutar /sacar para {character.name}")

# Exportamos la lista de comandos de este módulo.
INTERACTION_COMMANDS = [
    CmdGet(),
    CmdDrop(),
    CmdPut(),
    CmdTake(),
]