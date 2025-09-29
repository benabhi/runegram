# src/utils/presenters.py

from aiogram import types
from collections import Counter

from src.models.room import Room
# La importación de Item ya no es estrictamente necesaria aquí, pero es buena práctica mantenerla
# por si en el futuro se añaden más funciones de formato relacionadas con items.
from src.models.item import Item
from src.db import async_session_factory
from src.services import player_service


async def format_room(room: Room) -> str:
    """
    Construye y formatea la descripción completa de una sala para ser mostrada al jugador.
    Esta función está diseñada para ser fácilmente extensible.
    """
    parts = []

    # 1. Título de la Sala (en negrita)
    parts.append(f"<b>{room.name}</b>")

    # 2. Descripción principal
    # Usamos strip() para quitar espacios en blanco al inicio/final que puedan venir de la BD
    parts.append(room.description.strip())

    # 3. Items en la sala
    if room.items:
        # Ahora llamamos al método .get_name() directamente desde cada objeto Item
        item_names = [item.get_name() for item in room.items]

        # Agrupamos items idénticos para mostrarlos de forma compacta (ej: una moneda de oro (3))
        item_counts = Counter(item_names)
        formatted_items = [f"{name} ({count})" if count > 1 else name for name, count in item_counts.items()]
        items_str = ", ".join(formatted_items)
        parts.append(f"\n<b>Ves aquí:</b> {items_str}.")

    # 4. Salidas
    if room.exits_from:
        exits_list = sorted([exit_obj.name.capitalize() for exit_obj in room.exits_from])
        exits_str = ", ".join(exits_list)
        parts.append(f"\n<b>Salidas:</b> [ {exits_str} ]")
    else:
        parts.append("\n<b>Salidas:</b> [ Ninguna ]")

    description_body = "\n".join(parts)

    # Envolvemos el resultado final en etiquetas <pre> para un formato de monoespaciado
    return f"<pre>{description_body}</pre>"


async def show_current_room(message: types.Message):
    """
    Obtiene la sala actual del jugador y le muestra la descripción formateada.
    Esta función centraliza la lógica de "mirar" el entorno.
    """
    async with async_session_factory() as session:
        # Usamos el servicio para obtener la cuenta y sus relaciones precargadas
        account = await player_service.get_or_create_account(session, message.from_user.id)

        if not account.character or not account.character.room:
            # Esta es una salvaguarda.
            await message.answer("Parece que estás perdido en el vacío. Te hemos llevado a un lugar seguro.")
            return

        room = account.character.room
        # Usamos nuestro formateador para construir el texto de la sala
        formatted_room = await format_room(room)

        # Usamos parse_mode="HTML" para que Telegram entienda las etiquetas <pre> y <b>
        await message.answer(formatted_room, parse_mode="HTML")