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
from src.utils.presenters import show_current_room, format_item_look, format_inventory, format_who_list
from src.services import script_service, online_service, permission_service, broadcaster_service
from src.utils.pagination import paginate_list, format_pagination_footer
from src.templates import ICONS

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
                    # Cargar contained_items si es contenedor
                    if item.prototype.get("is_container"):
                        await session.refresh(item, attribute_names=['contained_items'])

                    # Usar el nuevo sistema de templates
                    response = format_item_look(item, can_interact=True)
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
                    # Cargar contained_items si es contenedor
                    if item.prototype.get("is_container"):
                        await session.refresh(item, attribute_names=['contained_items'])

                    # Usar el nuevo sistema de templates
                    response = format_item_look(item, can_interact=True)
                    await message.answer(response, parse_mode="HTML")

                    # Ejecutar script on_look si existe
                    if "on_look" in item.prototype.get("scripts", {}):
                        await script_service.execute_script(
                            script_string=item.prototype["scripts"]["on_look"],
                            session=session, character=character, target=item
                        )
                    return

            # 4. Buscar otros personajes en la sala (solo jugadores online).
            for other_char in character.room.characters:
                if other_char.id != character.id and target_string == other_char.name.lower():
                    # Verificar que el personaje esté activamente jugando (online)
                    if not await online_service.is_character_online(other_char.id):
                        await message.answer("No ves a nadie con ese nombre por aquí.")
                        return

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
    description = "Muestra tu inventario o el de un contenedor. Uso: /inv [contenedor|todo [página]]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            # CASO 1: Mirar el inventario propio (sin límites).
            if not args:
                # Cargar contained_items para todos los contenedores
                for item in character.items:
                    if item.prototype.get("is_container"):
                        await session.refresh(item, attribute_names=['contained_items'])

                # Usar el nuevo sistema de templates
                response = format_inventory(character.items, owner_name=None, is_container=False)
                await message.answer(response, parse_mode="HTML")
                return

            # CASO 2: Modo "todo" con paginación (inventario completo sin límites).
            if args[0].lower() == "todo":
                page = 1
                if len(args) > 1:
                    try:
                        page = int(args[1])
                    except ValueError:
                        await message.answer("Uso: /inv todo [número de página]")
                        return

                items = character.items

                if not items:
                    await message.answer(f"<pre>{ICONS['inventory']} No llevas nada.</pre>", parse_mode="HTML")
                    return

                # Paginar items
                pagination = paginate_list(items, page=page, per_page=30)

                # Construir output
                lines = [
                    f"{ICONS['inventory']} <b>Tu Inventario Completo</b>",
                    "─────────────────────────────"
                ]

                for idx, item in enumerate(pagination['items'], start=pagination['start_index']):
                    item_icon = item.prototype.get('display', {}).get('icon', ICONS['item'])
                    item_name = item.get_name()
                    lines.append(f"{idx}. {item_icon} {item_name}")

                # Agregar footer de paginación
                if pagination['total_pages'] > 1:
                    lines.append(format_pagination_footer(
                        pagination['page'],
                        pagination['total_pages'],
                        '/inv todo',
                        pagination['total_items']
                    ))

                output = "<pre>" + "\n".join(lines) + "</pre>"
                await message.answer(output, parse_mode="HTML")
                return

            # CASO 3: Mirar el inventario de un contenedor.
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

            # Usar el nuevo sistema de templates
            response = format_inventory(
                container.contained_items,
                owner_name=container.get_name(),
                is_container=True
            )
            await message.answer(response, parse_mode="HTML")

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
            "<b>Comandos de Listados</b>\n"
            "/items - Lista todos los items de la sala.\n"
            "/personajes - Lista todos los personajes aquí.\n"
            "/inv todo - Inventario completo con paginación.\n"
            "/quien todo - Lista completa de jugadores.\n\n"
            "Para moverte, usa /norte, /sur, etc."
        )
        await message.answer(f"<pre>{help_text}</pre>", parse_mode="HTML")

class CmdWho(Command):
    """Comando social que muestra una lista de personajes conectados."""
    names = ["quien", "who"]
    lock = ""
    description = "Muestra una lista de los jugadores conectados. Uso: /quien [todo [página]]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            online_characters = await online_service.get_online_characters(session)

            # CASO 1: Mostrar lista normal con límites
            if not args:
                # Usar el nuevo sistema de templates
                response = format_who_list(online_characters, viewer_character=character)
                await message.answer(response, parse_mode="HTML")
                return

            # CASO 2: Modo "todo" con paginación (lista completa sin límites)
            if args[0].lower() == "todo":
                page = 1
                if len(args) > 1:
                    try:
                        page = int(args[1])
                    except ValueError:
                        await message.answer("Uso: /quien todo [número de página]")
                        return

                # Filtrar para excluir al viewer
                filtered_chars = [char for char in online_characters if char.id != character.id]

                if not filtered_chars:
                    await message.answer(f"<pre>{ICONS['player']} Eres la única alma aventurera en este mundo ahora mismo.</pre>", parse_mode="HTML")
                    return

                # Ordenar por nombre
                filtered_chars.sort(key=lambda c: c.name)

                # Paginar personajes
                pagination = paginate_list(filtered_chars, page=page, per_page=30)

                # Construir output
                lines = [
                    f"{ICONS['player']} <b>Jugadores en Runegram ({len(online_characters)} conectados)</b>",
                    "─────────────────────────────"
                ]

                for idx, char in enumerate(pagination['items'], start=pagination['start_index']):
                    location = f" ({ICONS['room']} {char.room.name})" if char.room else ""
                    lines.append(f"{idx}. {char.name}{location}")

                # Agregar footer de paginación
                if pagination['total_pages'] > 1:
                    lines.append(format_pagination_footer(
                        pagination['page'],
                        pagination['total_pages'],
                        '/quien todo',
                        pagination['total_items']
                    ))

                output = "<pre>" + "\n".join(lines) + "</pre>"
                await message.answer(output, parse_mode="HTML")
                return

            # Si hay args pero no es "todo", mostrar mensaje de uso
            await message.answer("Uso: /quien [todo [página]]")

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


class CmdDisconnect(Command):
    """Comando para desconectarse inmediatamente del juego."""
    names = ["desconectar", "logout", "salir"]
    description = "Te desconecta inmediatamente del juego."
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            from src.services.online_service import redis_client, _get_last_seen_key, _get_offline_notified_key
            from datetime import timedelta

            # Eliminar last_seen para marcar como offline
            await redis_client.delete(_get_last_seen_key(character.id))

            # Establecer offline_notified para que se notifique la reconexión
            await redis_client.set(
                _get_offline_notified_key(character.id),
                "1",
                ex=timedelta(days=1)
            )

            await message.answer(
                "Te has desconectado del juego.\n\n"
                "Vuelve cuando quieras con cualquier comando. ¡Hasta pronto!"
            )

            logging.info(f"Personaje {character.name} se ha desconectado manualmente usando /desconectar")

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar desconectar.")
            logging.exception(f"Fallo al ejecutar /desconectar para {character.name}")


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

            # Verificar que el jugador objetivo esté activamente jugando (online)
            if not await online_service.is_character_online(target_character.id):
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
    CmdDisconnect(),
    CmdWhisper(),
]