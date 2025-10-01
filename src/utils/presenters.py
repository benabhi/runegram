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


async def format_room(room: Room) -> str:
    """
    Construye y formatea la descripción completa de una sala para ser
    mostrada al jugador.

    Args:
        room (Room): El objeto de la sala a formatear, con sus relaciones
                     (`items`, `exits_from`) ya cargadas.

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
            item_names = [item.get_name() for item in room.items]
            item_counts = Counter(item_names)
            formatted_items = [f"{name} ({count})" if count > 1 else name for name, count in item_counts.items()]
            items_str = ", ".join(formatted_items)
            parts.append(f"\n<b>Ves aquí:</b> {items_str}.")

        # 4. Salidas
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
            # Usamos nuestro formateador para construir el texto de la sala.
            formatted_room = await format_room(room)

            await message.answer(formatted_room, parse_mode="HTML")

    except Exception:
        await message.answer("❌ Ocurrió un error al mostrar tu ubicación actual.")
        logging.exception(f"Fallo en show_current_room para el usuario {message.from_user.id}")