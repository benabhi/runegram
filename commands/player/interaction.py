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
from src.services import item_service, command_service, player_service, permission_service, online_service

# --- Funciones de Ayuda (Compartidas en este módulo) ---

def find_item_in_list(item_name: str, item_list: list):
    """Busca un objeto en una lista por su nombre o keywords."""
    for item in item_list:
        if item_name in item.get_keywords() or item_name == item.get_name().lower():
            return item
    return None


def find_item_in_list_with_ordinal(
    search_term: str,
    item_list: list,
    enable_disambiguation: bool = True
) -> tuple:
    """
    Busca un item con soporte para ordinales y desambiguación.

    Soporta sintaxis de ordinales estándar de MUDs: "2.espada" busca la segunda espada.

    Args:
        search_term: Término de búsqueda. Puede ser:
                    - "espada" -> busca primera espada
                    - "2.espada" -> busca segunda espada (ordinal)
                    - "mochila" -> busca primera mochila
        item_list: Lista de items donde buscar
        enable_disambiguation: Si True, detecta ambigüedad y retorna mensaje de ayuda

    Returns:
        tuple: (item_encontrado | None, mensaje_error | None)
               - Si encuentra 1 item: (item, None)
               - Si hay duplicados sin ordinal: (None, mensaje_desambiguacion)
               - Si no encuentra nada: (None, None)
               - Si ordinal es inválido: (None, mensaje_error)

    Ejemplos:
        >>> find_item_in_list_with_ordinal("espada", items, True)
        # Si hay 1 espada: (item, None)
        # Si hay 3 espadas: (None, "Hay 3 'espada'. ¿Cuál?...")

        >>> find_item_in_list_with_ordinal("2.espada", items, True)
        # (segunda_espada, None) o (None, "No hay segunda espada")
    """
    search_term = search_term.lower().strip()

    # Detectar si hay ordinal en el formato "N.nombre"
    ordinal_match = re.match(r'^(\d+)\.(.+)$', search_term)

    if ordinal_match:
        # Sintaxis con ordinal: "2.espada"
        ordinal_num = int(ordinal_match.group(1))
        item_name = ordinal_match.group(2).strip()

        # Buscar todas las coincidencias
        matches = []
        for item in item_list:
            if item_name in item.get_keywords() or item_name == item.get_name().lower():
                matches.append(item)

        # Validar que el ordinal esté en rango
        if ordinal_num < 1:
            return None, f"El número debe ser 1 o mayor."

        if ordinal_num > len(matches):
            if len(matches) == 0:
                return None, None  # No hay items con ese nombre
            elif len(matches) == 1:
                return None, f"Solo hay 1 '{item_name}'."
            else:
                return None, f"Solo hay {len(matches)} '{item_name}'."

        # Retornar el item en la posición ordinal (ordinal_num - 1 porque es 1-indexed)
        return matches[ordinal_num - 1], None

    else:
        # Sin ordinal: buscar todas las coincidencias
        matches = []
        for item in item_list:
            if search_term in item.get_keywords() or search_term == item.get_name().lower():
                matches.append(item)

        if len(matches) == 0:
            return None, None  # No se encontró

        elif len(matches) == 1:
            return matches[0], None  # Exactamente uno, retornarlo

        else:
            # Múltiples coincidencias
            if enable_disambiguation:
                # Generar mensaje de desambiguación con ejemplos de uso
                disambiguation_msg = f"❓ Hay {len(matches)} '{search_term}'. ¿Cuál?\n\n"
                for idx, item in enumerate(matches, start=1):
                    item_icon = item.prototype.get('display', {}).get('icon', '📦')
                    disambiguation_msg += f"{idx}. {item_icon} {item.get_name()}\n"

                # Agregar ejemplos de uso
                disambiguation_msg += f"\n💡 Usa ordinales para especificar:\n"
                disambiguation_msg += f"<code>1.{search_term}</code> → primera {search_term}\n"
                if len(matches) >= 2:
                    disambiguation_msg += f"<code>2.{search_term}</code> → segunda {search_term}"

                return None, disambiguation_msg.strip()
            else:
                # Desambiguación deshabilitada, retornar el primero
                return matches[0], None


def create_disambiguation_message(
    items: list,
    action: str,
    search_term: str,
    preposition: str = None,
    target_term: str = None
) -> str:
    """
    Crea un mensaje de desambiguación claro con instrucciones de uso.

    Args:
        items: Lista de items duplicados
        action: Verbo del comando ("coger", "meter", "dejar")
        search_term: Término ambiguo ("espada")
        preposition: Preposición si aplica ("en", "de")
        target_term: Término del target si aplica ("mochila")

    Returns:
        str: Mensaje HTML formateado con opciones y ejemplos

    Ejemplo:
        >>> create_disambiguation_message(espadas, "coger", "espada")
        "❓ Hay 2 'espada'. ¿Cuál quieres coger?\n\n1. ⚔️ espada oxidada\n..."

        >>> create_disambiguation_message(pociones, "meter", "pocion", "en", "mochila")
        "❓ Hay 3 'pocion'. ¿Cuál quieres meter?\n\n1. 🧪 poción roja\n..."
    """
    msg = f"❓ Hay {len(items)} '{search_term}'. ¿Cuál quieres {action}?\n\n"

    # Listar items con números
    for idx, item in enumerate(items, start=1):
        item_icon = item.prototype.get('display', {}).get('icon', '📦')
        msg += f"{idx}. {item_icon} {item.get_name()}\n"

    # Agregar ejemplos de uso
    msg += f"\nUsa:"

    if preposition and target_term:
        # Comando con preposición: "meter X en Y"
        msg += f"\n<code>/{action} 1.{search_term} {preposition} {target_term}</code>"
        if len(items) >= 2:
            msg += f"\n<code>/{action} 2.{search_term} {preposition} {target_term}</code>"
    else:
        # Comando simple: "coger X"
        msg += f"\n<code>/{action} 1.{search_term}</code>"
        if len(items) >= 2:
            msg += f"\n<code>/{action} 2.{search_term}</code>"

    return msg

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

def parse_give_args(args: list[str]) -> tuple[str | None, str | None]:
    """
    Parsea argumentos del comando /dar: "objeto a personaje".
    Devuelve (nombre_objeto, nombre_personaje).
    """
    arg_string = " ".join(args).lower()
    match = re.search(r'\s(a)\s', arg_string)
    if match:
        parts = arg_string.split(' a ', 1)
        item_name = parts[0].strip()
        character_name = parts[1].strip()
        return item_name, character_name
    return None, None

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

            # Lógica para coger un objeto del suelo con soporte para ordinales
            item_to_get, error_msg = find_item_in_list_with_ordinal(
                item_name_to_get,
                character.room.items,
                enable_disambiguation=True
            )

            # Manejar desambiguación
            if error_msg:
                await message.answer(error_msg, parse_mode="HTML")
                return

            if not item_to_get:
                await message.answer("No ves eso por aquí.")
                return

            # Verificar locks con access type "get"
            locks = item_to_get.prototype.get("locks", "")
            lock_messages = item_to_get.prototype.get("lock_messages", {})
            can_pass, error_message = await permission_service.can_execute(
                character,
                locks,
                access_type="get",
                lock_messages=lock_messages
            )
            if not can_pass:
                await message.answer(error_message or "No puedes coger eso.")
                return

            await item_service.move_item_to_character(session, item_to_get.id, character.id)

            if item_to_get.prototype.get("grants_command_sets"):
                refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
                await command_service.update_telegram_commands(refreshed_character)

            # Mensaje al jugador
            await message.answer(f"Has cogido: {item_to_get.get_name()}")

            # Mensaje social a la sala
            from src.services import broadcaster_service
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=character.room_id,
                message_text=f"<i>{character.name} ha cogido {item_to_get.get_name()} del suelo.</i>",
                exclude_character_id=character.id
            )
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

            # Buscar con soporte para ordinales
            item_to_drop, error_msg = find_item_in_list_with_ordinal(
                item_to_drop_name,
                character.items,
                enable_disambiguation=True
            )

            # Manejar desambiguación
            if error_msg:
                await message.answer(error_msg, parse_mode="HTML")
                return

            if not item_to_drop:
                await message.answer("No llevas eso.")
                return

            await item_service.move_item_to_room(session, item_to_drop.id, character.room_id)

            if item_to_drop.prototype.get("grants_command_sets"):
                refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
                await command_service.update_telegram_commands(refreshed_character)

            # Mensaje al jugador
            await message.answer(f"Has dejado: {item_to_drop.get_name()}")

            # Mensaje social a la sala
            from src.services import broadcaster_service
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=character.room_id,
                message_text=f"<i>{character.name} ha dejado {item_to_drop.get_name()} en el suelo.</i>",
                exclude_character_id=character.id
            )
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

            # Buscar contenedor con soporte para ordinales
            available_containers = character.items + character.room.items
            container, container_error = find_item_in_list_with_ordinal(
                container_name,
                available_containers,
                enable_disambiguation=True
            )

            # Manejar desambiguación del contenedor
            if container_error:
                await message.answer(container_error, parse_mode="HTML")
                return

            if not container:
                await message.answer(f"No ves ningún '{container_name}' por aquí.")
                return

            if not container.prototype.get("is_container"):
                await message.answer(f"{container.get_name().capitalize()} no es un contenedor.")
                return

            # Verificar locks con access type "put"
            locks = container.prototype.get("locks", "")
            lock_messages = container.prototype.get("lock_messages", {})
            can_pass, error_message = await permission_service.can_execute(
                character,
                locks,
                access_type="put",
                lock_messages=lock_messages
            )
            if not can_pass:
                await message.answer(error_message or f"No puedes meter nada en {container.get_name()}.")
                return

            capacity = container.prototype.get("capacity", 999)
            await session.refresh(container, attribute_names=['contained_items'])
            if len(container.contained_items) >= capacity:
                await message.answer(f"{container.get_name().capitalize()} está lleno.")
                return

            # Buscar item con soporte para ordinales
            available_items = character.items + character.room.items
            item_to_store, item_error = find_item_in_list_with_ordinal(
                item_name,
                available_items,
                enable_disambiguation=True
            )

            # Manejar desambiguación del item
            if item_error:
                await message.answer(item_error, parse_mode="HTML")
                return

            if not item_to_store:
                await message.answer(f"No tienes ni ves ningún '{item_name}'.")
                return

            if item_to_store.id == container.id:
                await message.answer("No puedes meter un objeto dentro de sí mismo.")
                return

            await item_service.move_item_to_container(session, item_to_store.id, container.id)

            # Mensaje al jugador
            await message.answer(f"Guardas {item_to_store.get_name()} en {container.get_name()}.")

            # Mensaje social a la sala
            from src.services import broadcaster_service
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=character.room_id,
                message_text=f"<i>{character.name} guarda {item_to_store.get_name()} en {container.get_name()}.</i>",
                exclude_character_id=character.id
            )

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

            # Buscar contenedor con soporte para ordinales
            available_containers = character.items + character.room.items
            container, container_error = find_item_in_list_with_ordinal(
                container_name,
                available_containers,
                enable_disambiguation=True
            )

            # Manejar desambiguación del contenedor
            if container_error:
                await message.answer(container_error, parse_mode="HTML")
                return

            if not container:
                await message.answer(f"No ves ningún '{container_name}' por aquí.")
                return

            # Verificar locks con access type "take"
            locks = container.prototype.get("locks", "")
            lock_messages = container.prototype.get("lock_messages", {})
            can_pass, error_message = await permission_service.can_execute(
                character,
                locks,
                access_type="take",
                lock_messages=lock_messages
            )
            if not can_pass:
                await message.answer(error_message or f"No puedes sacar nada de {container.get_name()}.")
                return

            # Buscar item con soporte para ordinales
            await session.refresh(container, attribute_names=['contained_items'])
            item_to_take, item_error = find_item_in_list_with_ordinal(
                item_name,
                container.contained_items,
                enable_disambiguation=True
            )

            # Manejar desambiguación del item
            if item_error:
                await message.answer(item_error, parse_mode="HTML")
                return

            if not item_to_take:
                await message.answer(f"No ves ningún '{item_name}' en {container.get_name()}.")
                return

            await item_service.move_item_to_character(session, item_to_take.id, character.id)

            # Mensaje al jugador
            await message.answer(f"Sacas {item_to_take.get_name()} de {container.get_name()}.")

            # Mensaje social a la sala
            from src.services import broadcaster_service
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=character.room_id,
                message_text=f"<i>{character.name} saca {item_to_take.get_name()} de {container.get_name()}.</i>",
                exclude_character_id=character.id
            )

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar sacar el objeto.")
            logging.exception(f"Fallo al ejecutar /sacar para {character.name}")

class CmdGive(Command):
    """Comando para dar un objeto a otro personaje."""
    names = ["dar", "give"]
    description = "Da un objeto a otro personaje. Uso: /dar <objeto> a <personaje>"
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            item_name, target_name = parse_give_args(args)
            if not item_name or not target_name:
                await message.answer("Uso: /dar <objeto> a <personaje>\nEjemplo: /dar espada a Gandalf")
                return

            # Buscar el objeto en el inventario con soporte para ordinales
            item_to_give, item_error = find_item_in_list_with_ordinal(
                item_name,
                character.items,
                enable_disambiguation=True
            )

            # Manejar desambiguación del item
            if item_error:
                await message.answer(item_error, parse_mode="HTML")
                return

            if not item_to_give:
                await message.answer(f"No tienes ningún '{item_name}'.")
                return

            # Buscar el personaje target en la sala
            target_character = None
            for other_char in character.room.characters:
                if other_char.id != character.id and target_name == other_char.name.lower():
                    target_character = other_char
                    break

            if not target_character:
                await message.answer(f"No ves a '{target_name}' por aquí.")
                return

            # Verificar que el personaje target esté online
            if not await online_service.is_character_online(target_character.id):
                await message.answer(f"{target_character.name} no está disponible en este momento.")
                return

            # Transferir el objeto
            await item_service.move_item_to_character(session, item_to_give.id, target_character.id)

            # Mensaje al que da
            await message.answer(f"Le das {item_to_give.get_name()} a {target_character.name}.")

            # Mensaje al que recibe (notificación privada)
            from src.services import broadcaster_service
            await broadcaster_service.send_message_to_character(
                target_character,
                f"<i>{character.name} te da {item_to_give.get_name()}.</i>"
            )

            # Mensaje social a la sala (excluyendo a ambos participantes)
            # broadcaster_service ya filtra desconectados automáticamente
            for other_char in character.room.characters:
                # Excluir al que da y al que recibe
                if other_char.id != character.id and other_char.id != target_character.id:
                    # Verificar que esté online (aunque broadcaster ya lo hace, doble verificación)
                    if await online_service.is_character_online(other_char.id):
                        await broadcaster_service.send_message_to_character(
                            other_char,
                            f"<i>{character.name} le da {item_to_give.get_name()} a {target_character.name}.</i>"
                        )

            # Actualizar comandos del que da si el item otorgaba command sets
            if item_to_give.prototype.get("grants_command_sets"):
                refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
                await command_service.sync_telegram_commands(refreshed_character)

            # Actualizar comandos del que recibe si el item otorga command sets
            if item_to_give.prototype.get("grants_command_sets"):
                refreshed_target = await player_service.get_character_with_relations_by_id(session, target_character.id)
                await command_service.sync_telegram_commands(refreshed_target)

            await session.commit()

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar dar el objeto.")
            logging.exception(f"Fallo al ejecutar /dar para {character.name}")

# Exportamos la lista de comandos de este módulo.
INTERACTION_COMMANDS = [
    CmdGet(),
    CmdDrop(),
    CmdPut(),
    CmdTake(),
    CmdGive(),
]