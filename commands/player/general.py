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
from src.models import Character, Item, Exit, Room
from src.utils.presenters import show_current_room, format_item_look, format_inventory, format_who_list
from src.services import script_service, online_service, permission_service, broadcaster_service
from src.services import event_service, EventType, EventPhase, EventContext
from src.utils.pagination import paginate_list, format_pagination_footer
from src.templates import ICONS
from src.config import settings

# Re-importamos funciones de búsqueda aquí ya que CmdInventory y CmdLook las necesitan.
from .interaction import find_item_in_list, find_item_in_list_with_ordinal

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

            # 2. Buscar en objetos (sala + inventario) con soporte para ordinales.
            available_items = character.room.items + character.items
            item_to_look, item_error = find_item_in_list_with_ordinal(
                target_string,
                available_items,
                enable_disambiguation=True
            )

            # Manejar desambiguación
            if item_error:
                await message.answer(item_error, parse_mode="HTML")
                return

            if item_to_look:
                # FASE BEFORE: Permite cancelar o modificar la acción de mirar
                before_context = EventContext(
                    session=session,
                    character=character,
                    target=item_to_look,
                    room=character.room
                )

                before_result = await event_service.trigger_event(
                    event_type=EventType.ON_LOOK,
                    phase=EventPhase.BEFORE,
                    context=before_context
                )

                # Si un script BEFORE cancela la acción, detener
                if before_result.cancel_action:
                    await message.answer(before_result.message or "No puedes mirar eso ahora.")
                    return

                # Cargar contained_items si es contenedor
                if item_to_look.prototype.get("is_container"):
                    await session.refresh(item_to_look, attribute_names=['contained_items'])

                # Usar el nuevo sistema de templates (acción principal)
                response = format_item_look(item_to_look, can_interact=True)
                await message.answer(response, parse_mode="HTML")

                # FASE AFTER: Ejecutar efectos después de mirar
                after_context = EventContext(
                    session=session,
                    character=character,
                    target=item_to_look,
                    room=character.room
                )

                await event_service.trigger_event(
                    event_type=EventType.ON_LOOK,
                    phase=EventPhase.AFTER,
                    context=after_context
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

            # 5. Buscar si es una dirección/salida para ver sala aledaña.
            from src.utils.presenters import format_room
            target_exit = next(
                (exit_obj for exit_obj in character.room.exits_from if exit_obj.name == target_string),
                None
            )

            if target_exit and target_exit.to_room:
                # Cargar sala destino con relaciones necesarias
                from sqlalchemy import select
                from sqlalchemy.orm import selectinload
                from src.models import Room

                result = await session.execute(
                    select(Room)
                    .where(Room.id == target_exit.to_room_id)
                    .options(
                        selectinload(Room.items),
                        selectinload(Room.characters).selectinload(Character.account),
                        selectinload(Room.exits_from).selectinload(Exit.to_room)
                    )
                )
                adjacent_room = result.scalar_one_or_none()

                if adjacent_room:
                    # Formatear y mostrar la sala (format_room filtra personajes online internamente)
                    room_description = await format_room(
                        adjacent_room,
                        viewing_character=character
                    )
                    await message.answer(
                        f"🔭 <b>Miras hacia el {target_string}...</b>\n{room_description}",
                        parse_mode="HTML"
                    )
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

class CmdEmotion(Command):
    """Comando para realizar emotes/emociones de roleplay."""
    names = ["emocion", "emote", "me"]
    lock = ""
    description = "Expresa una emoción o acción. Uso: /emocion se rasca la nariz"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            await message.answer("Uso: /emocion <acción>\nEjemplo: /emocion se rasca la nariz")
            return

        emote_text = " ".join(args)

        # Mensaje completo: "Benabhi se rasca la nariz"
        full_emote = f"<i>{character.name} {emote_text}</i>"

        # Enviar a todos en la sala (incluyendo al jugador que lo ejecutó)
        await broadcaster_service.send_message_to_room(
            session=session,
            room_id=character.room_id,
            message_text=full_emote,
            exclude_character_id=None  # No excluir a nadie, todos lo ven
        )

class CmdInventory(Command):
    """Comando para mostrar el inventario del jugador o el de un contenedor con paginación automática."""
    names = ["inventario", "inv", "i"]
    description = "Muestra tu inventario o el de un contenedor. Uso: /inv [contenedor] [página]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            from src.utils.paginated_output import send_paginated_simple, parse_page_from_args

            # CASO 1: Inventario propio con paginación automática
            if not args:
                items = character.items

                if not items:
                    await message.answer(f"{ICONS['inventory']} No llevas nada.")
                    return

                # Función de formato para cada item
                def format_inv_item(item):
                    item_icon = item.prototype.get('display', {}).get('icon', ICONS['item'])
                    container_info = ""
                    if item.prototype.get("is_container") and item.contained_items:
                        container_info = f" ({len(item.contained_items)} {len(item.contained_items) if len(item.contained_items) != 1 else ''} {'items' if len(item.contained_items) != 1 else 'item'})"
                    return f"{item_icon} {item.get_name()}{container_info}"

                # Cargar contained_items para contenedores (para el contador)
                for item in items:
                    if item.prototype.get("is_container"):
                        await session.refresh(item, attribute_names=['contained_items'])

                # Enviar lista paginada con botones (página 1 por defecto)
                await send_paginated_simple(
                    message=message,
                    items=items,
                    page=1,
                    callback_action="pg_inv",
                    format_func=format_inv_item,
                    header="Tu Inventario",
                    per_page=settings.pagination_items_per_page,
                    icon=ICONS['inventory']
                )
                return

            # CASO 2: Si el primer argumento es un número, es página del inventario propio
            if args[0].isdigit():
                page = parse_page_from_args(args, default=1)
                items = character.items

                if not items:
                    await message.answer(f"{ICONS['inventory']} No llevas nada.")
                    return

                # Función de formato para cada item
                def format_inv_item(item):
                    item_icon = item.prototype.get('display', {}).get('icon', ICONS['item'])
                    container_info = ""
                    if item.prototype.get("is_container") and item.contained_items:
                        container_info = f" ({len(item.contained_items)} {'items' if len(item.contained_items) != 1 else 'item'})"
                    return f"{item_icon} {item.get_name()}{container_info}"

                # Cargar contained_items para contenedores
                for item in items:
                    if item.prototype.get("is_container"):
                        await session.refresh(item, attribute_names=['contained_items'])

                # Enviar lista paginada con botones
                await send_paginated_simple(
                    message=message,
                    items=items,
                    page=page,
                    callback_action="pg_inv",
                    format_func=format_inv_item,
                    header="Tu Inventario",
                    per_page=settings.pagination_items_per_page,
                    icon=ICONS['inventory']
                )
                return

            # CASO 3: Mirar el inventario de un contenedor con paginación
            # Detectar si el último argumento es un número (página)
            page = 1
            container_args = args
            if len(args) > 1 and args[-1].isdigit():
                page = int(args[-1])
                container_args = args[:-1]

            container_name = " ".join(container_args).lower()
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

            if not container.contained_items:
                await message.answer(f"{ICONS['inventory']} El inventario de {container.get_name()} está vacío.")
                return

            # Función de formato para cada item del contenedor
            def format_container_item(item):
                item_icon = item.prototype.get('display', {}).get('icon', ICONS['item'])
                return f"{item_icon} {item.get_name()}"

            # Enviar lista paginada con botones
            await send_paginated_simple(
                message=message,
                items=container.contained_items,
                page=page,
                callback_action="pg_inv_cont",
                format_func=format_container_item,
                header=f"Inventario de {container.get_name()}",
                per_page=settings.pagination_items_per_page,
                icon=ICONS['inventory'],
                container_id=container.id  # Para callbacks
            )

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
            "/inventario - Muestra los objetos que llevas (con paginación).\n"
            "/decir [mensaje] - Hablas a la gente en tu misma sala.\n"
            "/coger [objeto] - Recoges un objeto del suelo.\n"
            "/dejar [objeto] - Dejas un objeto en el suelo.\n"
            "/quien - Muestra quién está conectado (con paginación).\n"
            "/canales - Gestiona tus suscripciones a canales.\n\n"
            "<b>Comandos de Listados</b>\n"
            "/items - Lista todos los items de la sala.\n"
            "/personajes - Lista todos los personajes aquí.\n"
            "/inv 2 - Ver página 2 de tu inventario.\n"
            "/quien 2 - Ver página 2 de jugadores.\n\n"
            "Para moverte, usa /norte, /sur, etc."
        )
        await message.answer(f"<pre>{help_text}</pre>", parse_mode="HTML")

class CmdWho(Command):
    """Comando social que muestra una lista de personajes conectados con paginación automática."""
    names = ["quien", "who"]
    lock = ""
    description = "Muestra una lista de los jugadores conectados. Uso: /quien [página]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            from src.utils.paginated_output import send_paginated_simple, parse_page_from_args

            online_characters = await online_service.get_online_characters(session)

            # Filtrar para excluir al viewer
            filtered_chars = [char for char in online_characters if char.id != character.id]

            if not filtered_chars:
                await message.answer(f"{ICONS['player']} Eres la única alma aventurera en este mundo ahora mismo.")
                return

            # Ordenar por nombre
            filtered_chars.sort(key=lambda c: c.name)

            # Parsear página (si no se proporciona, default = 1)
            page = parse_page_from_args(args, default=1)

            # Obtener mensajes AFK desde Redis para formateo
            from src.services.online_service import redis_client
            afk_messages = {}
            for char in filtered_chars:
                afk_key = f"afk:{char.id}"
                afk_msg = await redis_client.get(afk_key)
                if afk_msg:
                    afk_messages[char.id] = afk_msg.decode('utf-8') if isinstance(afk_msg, bytes) else afk_msg

            # Función de formato para cada personaje
            def format_who_char(char):
                location = f" ({ICONS['room']} {char.room.name})" if char.room else ""
                afk_status = ""
                if char.id in afk_messages:
                    afk_status = f" [AFK: {afk_messages[char.id]}]"
                return f"{char.name}{location}{afk_status}"

            # Enviar lista paginada con botones
            await send_paginated_simple(
                message=message,
                items=filtered_chars,
                page=page,
                callback_action="pg_who",
                format_func=format_who_char,
                header=f"Jugadores en Runegram ({len(online_characters)} conectados)",
                per_page=settings.pagination_items_per_page,
                icon=ICONS['player']
            )

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

            # Eliminar last_seen para marcar como offline
            await redis_client.delete(_get_last_seen_key(character.id))

            # Establecer offline_notified para que se notifique la reconexión
            await redis_client.set(
                _get_offline_notified_key(character.id),
                "1",
                ex=settings.offline_notified_ttl
            )

            await message.answer(
                "Te has desconectado del juego.\n\n"
                "Vuelve cuando quieras con cualquier comando. ¡Hasta pronto!"
            )

            logging.info(f"Personaje {character.name} se ha desconectado manualmente usando /desconectar")

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar desconectar.")
            logging.exception(f"Fallo al ejecutar /desconectar para {character.name}")

class CmdAFK(Command):
    """Comando para ponerse AFK (Away From Keyboard) manualmente con mensaje opcional."""
    names = ["afk"]
    description = "Te marca como AFK con un mensaje opcional. Uso: /afk [mensaje]"
    lock = ""

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            from src.services.online_service import redis_client

            afk_message = " ".join(args) if args else "AFK"

            # Guardar mensaje AFK en Redis (con TTL de 24 horas)
            afk_key = f"afk:{character.id}"
            await redis_client.set(afk_key, afk_message, ex=86400)  # 24 horas

            # Mensaje de confirmación
            await message.answer(
                f"✅ Ahora estás AFK: {afk_message}\n\n"
                "Otros jugadores verán tu estado en /quien.\n"
                "Usa cualquier comando para volver."
            )

            logging.info(f"Personaje {character.name} se puso AFK: {afk_message}")

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar ponerte AFK.")
            logging.exception(f"Fallo al ejecutar /afk para {character.name}")

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
    CmdEmotion(),
    CmdInventory(),
    CmdHelp(),
    CmdWho(),
    CmdPray(),
    CmdDisconnect(),
    CmdAFK(),
    CmdWhisper(),
]