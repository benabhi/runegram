# commands/player/general.py
"""
Módulo de Comandos Generales del Jugador.

Este archivo agrupa los comandos más básicos y fundamentales que un jugador
utiliza para interactuar con el mundo y obtener información esencial sobre su
entorno y su personaje.

Estos comandos están disponibles para todos los jugadores en todo momento.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from collections import Counter

from commands.command import Command
from src.models import Character
from src.utils.presenters import show_current_room
from src.services import script_service, online_service, permission_service

# Re-importamos `find_item_in_list` aquí ya que CmdInventory lo necesita.
from .interaction import find_item_in_list

class CmdLook(Command):
    """
    Comando para observar el entorno, objetos, personajes o detalles.
    """
    names = ["mirar", "m", "l"]
    lock = ""
    description = "Observa tu entorno o un objeto/personaje/detalle específico."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            if not args:
                await show_current_room(message)
                return

            target_string = " ".join(args).lower()

            # 1. Buscar en los detalles de la sala.
            room_details = character.room.prototype.get("details", {})
            for detail_key, detail_data in room_details.items():
                if target_string in detail_data.get("keywords", []):
                    await message.answer(f"<pre>{detail_data['description']}</pre>", parse_mode="HTML")
                    return

            # 2. Buscar en los objetos de la sala.
            for item in character.room.items:
                if target_string in item.get_keywords() or target_string == item.get_name().lower():
                    # Descripción del objeto
                    response = f"<pre>{item.get_description()}</pre>"

                    # Si es un contenedor, mostrar su contenido
                    if item.prototype.get("is_container"):
                        await session.refresh(item, attribute_names=['contained_items'])
                        if item.contained_items:
                            item_names = [inner_item.get_name() for inner_item in item.contained_items]
                            item_counts = Counter(item_names)
                            formatted_items = [f" - {name}" + (f" ({count})" if count > 1 else "")
                                             for name, count in item_counts.items()]
                            items_str = "\n".join(formatted_items)
                            response += f"\n\n<b>Contiene:</b>\n{items_str}"
                        else:
                            response += f"\n\n<b>Está vacío.</b>"

                    await message.answer(response, parse_mode="HTML")

                    # Ejecutar script on_look si existe
                    if "on_look" in item.prototype.get("scripts", {}):
                        await script_service.execute_script(
                            script_string=item.prototype["scripts"]["on_look"],
                            session=session, character=character, target=item
                        )
                    return

            # 3. Buscar en el inventario del personaje.
            for item in character.items:
                if target_string in item.get_keywords() or target_string == item.get_name().lower():
                    # Descripción del objeto
                    response = f"<pre>{item.get_description()}</pre>"

                    # Si es un contenedor, mostrar su contenido
                    if item.prototype.get("is_container"):
                        await session.refresh(item, attribute_names=['contained_items'])
                        if item.contained_items:
                            item_names = [inner_item.get_name() for inner_item in item.contained_items]
                            item_counts = Counter(item_names)
                            formatted_items = [f" - {name}" + (f" ({count})" if count > 1 else "")
                                             for name, count in item_counts.items()]
                            items_str = "\n".join(formatted_items)
                            response += f"\n\n<b>Contiene:</b>\n{items_str}"
                        else:
                            response += f"\n\n<b>Está vacío.</b>"

                    await message.answer(response, parse_mode="HTML")

                    # Ejecutar script on_look si existe
                    if "on_look" in item.prototype.get("scripts", {}):
                        await script_service.execute_script(
                            script_string=item.prototype["scripts"]["on_look"],
                            session=session, character=character, target=item
                        )
                    return

            # 4. Buscar otros personajes en la sala.
            for other_char in character.room.characters:
                if other_char.id != character.id and target_string == other_char.name.lower():
                    await message.answer(f"<pre>{other_char.get_description()}</pre>", parse_mode="HTML")
                    return

            # Si no se encontró nada, dar un mensaje amigable
            await message.answer("No ves eso por aquí.")

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar mirar.")
            logging.exception(f"Fallo al ejecutar /mirar para {character.name}")

class CmdSay(Command):
    """Comando para que el personaje hable a otros en la misma sala."""
    names = ["decir", "'"]
    lock = ""
    description = "Habla con las personas que están en tu misma sala."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            await message.answer("¿Qué quieres decir?")
            return

        say_text = " ".join(args)

        # Confirmar al jugador que habló
        await message.answer(f"Dices: {say_text}")

        # Notificar a todos los demás en la sala
        await broadcaster_service.send_message_to_room(
            session=session,
            room_id=character.room_id,
            message_text=f"<i>{character.name} dice: {say_text}</i>",
            exclude_character_id=character.id
        )

class CmdInventory(Command):
    """Comando para mostrar el inventario del jugador o el de un contenedor."""
    names = ["inventario", "inv", "i"]
    description = "Muestra tu inventario o el de un contenedor. Uso: /inv [contenedor]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            # CASO 1: Mirar el inventario propio.
            if not args:
                inventory = character.items
                if not inventory:
                    response = "No llevas nada."
                else:
                    # Mostrar cantidad de items en contenedores
                    items_list = []
                    for item in inventory:
                        item_display = f" - {item.get_name()}"

                        # Si es un contenedor, mostrar cuántos items tiene
                        if item.prototype.get("is_container"):
                            await session.refresh(item, attribute_names=['contained_items'])
                            if item.contained_items:
                                item_count = len(item.contained_items)
                                item_display += f" ({item_count} {'item' if item_count == 1 else 'items'})"

                        items_list.append(item_display)

                    items_str = "\n".join(items_list)
                    response = f"<b>Llevas lo siguiente:</b>\n{items_str}"
                await message.answer(f"<pre>{response}</pre>", parse_mode="HTML")
                return

            # CASO 2: Mirar el inventario de un contenedor.
            container_name = " ".join(args).lower()
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
                await message.answer(f"No puedes ver el contenido de {container.get_name()}.")
                return

            await session.refresh(container, attribute_names=['contained_items'])
            inventory = container.contained_items
            if not inventory:
                response = f"{container.get_name().capitalize()} está vacío."
            else:
                item_names = [item.get_name() for item in inventory]
                item_counts = Counter(item_names)
                formatted_items = [f" - {name}" + (f" ({count})" if count > 1 else "") for name, count in item_counts.items()]
                items_str = "\n".join(formatted_items)
                response = f"<b>En {container.get_name()} ves:</b>\n{items_str}"

            await message.answer(f"<pre>{response}</pre>", parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al mostrar el inventario.")
            logging.exception(f"Fallo al ejecutar /inventario para {character.name}")


class CmdHelp(Command):
    """Comando para mostrar un mensaje de ayuda básico."""
    names = ["ayuda", "help"]
    lock = ""
    description = "Muestra una lista con los comandos básicos del juego."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        help_text = (
            "<b>Comandos Básicos de Runegram</b>\n"
            "---------------------------------\n"
            "/mirar - Muestra la descripción de tu entorno.\n"
            "/inventario - Muestra los objetos que llevas.\n"
            "/decir [mensaje] - Hablas a la gente en tu misma sala.\n"
            "/coger [objeto] - Recoges un objeto del suelo.\n"
            "/dejar [objeto] - Dejas un objeto en el suelo.\n"
            "/quien - Muestra quién está conectado.\n"
            "/canales - Gestiona tus suscripciones a canales.\n\n"
            "Para moverte, usa /norte, /sur, etc."
        )
        await message.answer(f"<pre>{help_text}</pre>", parse_mode="HTML")

class CmdWho(Command):
    """Comando social que muestra una lista de personajes conectados."""
    names = ["quien", "who"]
    lock = ""
    description = "Muestra una lista de los jugadores conectados."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            online_characters = await online_service.get_online_characters(session)

            if not online_characters or (len(online_characters) == 1 and online_characters[0].id == character.id):
                await message.answer("Eres la única alma aventurera en este mundo ahora mismo.")
                return

            response_lines = [f"<b>Hay {len(online_characters)} aventureros en Runegram:</b>"]
            for char in sorted(online_characters, key=lambda c: c.name):
                response_lines.append(f"- {char.name}")

            response_text = "\n".join(response_lines)
            await message.answer(f"<pre>{response_text}</pre>", parse_mode="HTML")
        except Exception:
            await message.answer("❌ Ocurrió un error al obtener la lista de jugadores.")
            logging.exception(f"Fallo al ejecutar /quien para {character.name}")

class CmdPray(Command):
    """Comando que permite al jugador rezar a los dioses."""
    names = ["orar", "rezar"]
    description = "Rezas a los dioses en busca de inspiración."
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            response_text = "Bajas la cabeza y murmuras una plegaria. Sientes una cálida sensación de esperanza."
            await message.answer(response_text)
        except Exception:
            await message.answer("❌ Ocurrió un error al intentar procesar tu plegaria.")
            logging.exception(f"Fallo al ejecutar /orar para {character.name}")


class CmdWhisper(Command):
    """Comando para enviar un mensaje privado a un jugador en la misma sala."""
    names = ["susurrar", "whisper"]
    description = "Susurra un mensaje privado a un jugador en tu sala. Uso: /susurrar <jugador> <mensaje>"
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            if len(args) < 2:
                await message.answer("Uso: /susurrar <jugador> <mensaje>")
                return

            target_name = args[0].lower()
            whisper_text = " ".join(args[1:])

            # Buscar el jugador objetivo en la misma sala
            target_character = None
            for other_char in character.room.characters:
                if other_char.id != character.id and other_char.name.lower() == target_name:
                    target_character = other_char
                    break

            if not target_character:
                await message.answer(f"No ves a ningún '{args[0]}' por aquí.")
                return

            # Cargar la relación account del target antes de enviar mensaje
            await session.refresh(target_character, ["account"])

            # Enviar el mensaje privado al jugador objetivo
            from src.services import broadcaster_service
            await broadcaster_service.send_message_to_character(
                target_character,
                f"<i>{character.name} te susurra: \"{whisper_text}\"</i>"
            )

            # Confirmar al emisor
            await message.answer(f"<i>Le susurras a {target_character.name}: \"{whisper_text}\"</i>", parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar susurrar.")
            logging.exception(f"Fallo al ejecutar /susurrar para {character.name}")


# Exportamos la lista de comandos de este módulo.
GENERAL_COMMANDS = [
    CmdLook(),
    CmdSay(),
    CmdInventory(),
    CmdHelp(),
    CmdWho(),
    CmdPray(),
    CmdWhisper(),
]