# src/utils/presenters.py
"""
Módulo de Utilidades de Presentación (Presenters).

Este archivo contiene funciones cuya única responsabilidad es tomar los objetos
de datos del juego (como `Room`, `Item`, `Character`) y convertirlos en texto
formateado listo para ser mostrado al jugador en Telegram.

Esta capa de "presentación" separa la lógica de cómo se ven las cosas (formato
HTML, colores, etc.) de la lógica de negocio del juego (que reside en los
servicios).

ACTUALIZACIÓN: Ahora utiliza el sistema de templates de Jinja2 para mantener
formatos consistentes y permitir personalización desde los prototipos.
"""

import logging
from aiogram import types
from collections import Counter

from src.models.room import Room
from src.models.character import Character
from src.models.item import Item
from src.db import async_session_factory
from src.services import player_service
from src.templates import render_template, ICONS, get_direction_icon
from src.config import settings


async def format_room(
    room: Room,
    viewing_character=None,
    max_items: int = None,
    max_characters: int = None
) -> str:
    """
    Construye y formatea la descripción completa de una sala para ser
    mostrada al jugador.

    Ahora utiliza el sistema de templates para mantener consistencia visual.

    Args:
        room (Room): El objeto de la sala a formatear, con sus relaciones
                     (`items`, `exits_from`, `characters`) ya cargadas.
        viewing_character (Character, optional): El personaje que está mirando,
                                                  para excluirlo de la lista de personajes.
        max_items (int, optional): Máximo de items a mostrar. Default: settings.max_room_items_display
        max_characters (int, optional): Máximo de personajes a mostrar. Default: settings.max_room_characters_display

    Returns:
        str: Un string formateado con HTML listo para ser enviado.
    """
    try:
        # Usar valores por defecto de config si no se especifican
        if max_items is None:
            max_items = settings.max_room_items_display
        if max_characters is None:
            max_characters = settings.max_room_characters_display

        # Preparar contexto para el template
        context = {
            'room': room,
            'character': viewing_character,
            'display': room.prototype.get('display', {}) if room.prototype else {},
            'max_items': max_items,
            'max_characters': max_characters,
            'icon': lambda key: ICONS.get(key, ''),
            'get_direction_icon': get_direction_icon,
        }

        # Verificar si hay un template personalizado en el prototipo
        custom_template = None
        if room.prototype:
            custom_template = room.prototype.get('display', {}).get('template')

        # Renderizar con template personalizado o default
        template_name = custom_template if custom_template else 'room.html.j2'

        return render_template(template_name, **context)

    except Exception:
        logging.exception(f"Error al formatear la descripción de la sala ID {room.id}")
        return "<pre><b>Error:</b> No se pudo mostrar la descripción de la sala.</pre>"


def format_inventory(
    items: list[Item],
    owner_name: str = None,
    is_container: bool = False,
    max_items: int = None
) -> str:
    """
    Formatea una lista de items como inventario.

    Args:
        items: Lista de objetos Item
        owner_name: Nombre del dueño del inventario (opcional)
        is_container: Si True, adapta el mensaje para contenedores
        max_items: Máximo de items a mostrar. Default: settings.max_inventory_display o max_container_display

    Returns:
        str: HTML formateado del inventario
    """
    try:
        # Usar valores por defecto de config si no se especifican
        if max_items is None:
            max_items = settings.max_container_display if is_container else settings.max_inventory_display

        context = {
            'items': items,
            'owner_name': owner_name,
            'is_container': is_container,
            'max_items': max_items,
            'icon': lambda key: ICONS.get(key, ''),
        }

        return render_template('inventory.html.j2', **context)

    except Exception:
        logging.exception("Error al formatear inventario")
        return "<pre>❌ Error al mostrar el inventario.</pre>"


def format_character(character: Character) -> str:
    """
    Formatea la información de un personaje (hoja de personaje).

    Args:
        character: Objeto Character con relaciones cargadas

    Returns:
        str: HTML formateado con información del personaje
    """
    try:
        context = {
            'character': character,
            'icon': lambda key: ICONS.get(key, ''),
        }

        return render_template('character.html.j2', **context)

    except Exception:
        logging.exception(f"Error al formatear personaje {character.id if character else 'unknown'}")
        return "<pre>❌ Error al mostrar información del personaje.</pre>"


def format_item_look(item: Item, can_interact: bool = True, max_contained: int = None) -> str:
    """
    Formatea la descripción de un item cuando se mira.

    Args:
        item: Objeto Item a describir
        can_interact: Si True, muestra sugerencias de interacción
        max_contained: Máximo de items contenidos a mostrar. Default: settings.max_container_display

    Returns:
        str: HTML formateado con descripción del item
    """
    try:
        # Usar valores por defecto de config si no se especifican
        if max_contained is None:
            max_contained = settings.max_container_display

        context = {
            'item': item,
            'can_interact': can_interact,
            'max_contained': max_contained,
            'icon': lambda key: ICONS.get(key, ''),
        }

        # Verificar si hay template personalizado en el prototipo
        custom_template = None
        if item.prototype:
            custom_template = item.prototype.get('display', {}).get('template')

        template_name = custom_template if custom_template else 'item_look.html.j2'

        return render_template(template_name, **context)

    except Exception:
        logging.exception(f"Error al formatear item {item.id if item else 'unknown'}")
        return "<pre>❌ Error al mostrar el objeto.</pre>"


def format_who_list(
    characters: list[Character],
    viewer_character: Character = None,
    max_characters: int = None
) -> str:
    """
    Formatea la lista de personajes online.

    Args:
        characters: Lista de personajes conectados
        viewer_character: El personaje que está viendo la lista
        max_characters: Máximo de personajes a mostrar. Default: settings.max_who_display

    Returns:
        str: HTML formateado con lista de jugadores
    """
    try:
        # Usar valores por defecto de config si no se especifican
        if max_characters is None:
            max_characters = settings.max_who_display

        context = {
            'characters': characters,
            'viewer_character': viewer_character,
            'max_characters': max_characters,
            'icon': lambda key: ICONS.get(key, ''),
        }

        return render_template('who.html.j2', **context)

    except Exception:
        logging.exception("Error al formatear lista de jugadores")
        return "<pre>❌ Error al mostrar la lista de jugadores.</pre>"


async def show_current_room(message: types.Message):
    """
    Obtiene la sala actual del jugador y le muestra la descripción formateada.
    Esta función centraliza la lógica común de "mirar" el entorno.
    """
    try:
        async with async_session_factory() as session:
            # Usamos el servicio para obtener la cuenta y sus relaciones precargadas.
            account = await player_service.get_or_create_account(session, message.from_user.id)

            if not account or not account.character or not account.character.room:
                # Esta es una salvaguarda. No debería ocurrir en un flujo normal.
                await message.answer("Parece que estás perdido en el vacío. Te hemos llevado a un lugar seguro.")
                # Futuro: Aquí podríamos teletransportar al jugador a la sala de inicio.
                return

            room = account.character.room
            character = account.character
            # Usamos nuestro formateador para construir el texto de la sala.
            formatted_room = await format_room(room, viewing_character=character)

            await message.answer(formatted_room, parse_mode="HTML")

    except Exception:
        await message.answer("❌ Ocurrió un error al mostrar tu ubicación actual.")
        logging.exception(f"Fallo en show_current_room para el usuario {message.from_user.id}")