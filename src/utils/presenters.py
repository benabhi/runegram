# src/utils/presenters.py
"""
Módulo de Utilidades de Presentación (Presenters).

Este archivo contiene funciones cuya única responsabilidad es tomar los objetos
de datos del juego (como `Room`, `Item`, `Character`) y convertirlos en texto
formateado listo para ser mostrado al jugador en Telegram.

Esta capa de "presentación" separa la lógica de cómo se ven las cosas (formato
HTML, colores, etc.) de la lógica de negocio del juego (que reside en los
servicios).
"""

import logging
from aiogram import types
from collections import Counter

from src.models.room import Room
from src.db import async_session_factory
from src.services import player_service


async def format_room(room: Room, viewing_character=None) -> str:
    """
    Construye y formatea la descripción completa de una sala para ser
    mostrada al jugador.

    Args:
        room (Room): El objeto de la sala a formatear, con sus relaciones
                     (`items`, `exits_from`, `characters`) ya cargadas.
        viewing_character (Character, optional): El personaje que está mirando,
                                                  para excluirlo de la lista de personajes.

    Returns:
        str: Un string formateado con HTML (`<pre>`, `<b>`) listo para ser enviado.
    """
    try:
        parts = []

        # 1. Título de la Sala
        parts.append(f"<b>{room.name}</b>")

        # 2. Descripción principal
        parts.append(room.description.strip())

        # 3. Objetos en la sala
        if room.items:
            # Usamos `collections.Counter` para agrupar objetos idénticos.
            # Por ejemplo, tres objetos con `get_name()`="una moneda de oro"
            # se mostrarán como "una moneda de oro (3)".
            formatted_items = []
            for item in room.items:
                item_display = item.get_name()

                # Si el item es un contenedor, mostrar cuántos items tiene dentro
                if item.prototype.get("is_container"):
                    # Asumimos que contained_items ya está cargado
                    if hasattr(item, 'contained_items') and item.contained_items:
                        item_count = len(item.contained_items)
                        item_display = f"{item_display} ({item_count} {'item' if item_count == 1 else 'items'})"

                formatted_items.append(item_display)

            # Agrupar items idénticos
            item_counts = Counter(formatted_items)
            final_items = [f"{name} ({count})" if count > 1 else name for name, count in item_counts.items()]
            items_str = ", ".join(final_items)
            parts.append(f"\n<b>Ves aquí:</b> {items_str}.")

        # 4. Personajes en la sala
        if room.characters:
            other_characters = [char for char in room.characters
                              if not viewing_character or char.id != viewing_character.id]

            if other_characters:
                char_names = [char.name for char in other_characters]
                chars_str = ", ".join(char_names)
                parts.append(f"\n<b>También están aquí:</b> {chars_str}.")

        # 5. Salidas
        if room.exits_from:
            # Ordenamos las salidas alfabéticamente para una visualización consistente.
            exits_list = sorted([exit_obj.name.capitalize() for exit_obj in room.exits_from])
            exits_str = ", ".join(exits_list)
            parts.append(f"\n<b>Salidas:</b> [ {exits_str} ]")
        else:
            parts.append("\n<b>Salidas:</b> [ Ninguna ]")

        # Unimos todas las partes y las envolvemos en una etiqueta <pre>
        # para mantener el formato de monoespaciado y los saltos de línea.
        description_body = "\n".join(parts)
        return f"<pre>{description_body}</pre>"

    except Exception:
        logging.exception(f"Error al formatear la descripción de la sala ID {room.id}")
        return "<pre><b>Error:</b> No se pudo mostrar la descripción de la sala.</pre>"


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