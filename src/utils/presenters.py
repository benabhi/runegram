# src/utils/presenters.py
from aiogram import types
from collections import Counter

from src.models.room import Room
from src.models.item import Item
from src.db import async_session_factory
from src.services import player_service
from game_data.item_prototypes import ITEM_PROTOTYPES


def get_item_name(item: Item) -> str:
    """Obtiene el nombre de un item, usando override o el prototipo."""
    if item.name_override:
        return item.name_override
    return ITEM_PROTOTYPES.get(item.key, {}).get("name", "un objeto misterioso")

async def format_room(room: Room) -> str:
    """
    Construye y formatea la descripción completa de una sala.
    """
    parts = []
    parts.append(f"<b>{room.name}</b>")
    parts.append(room.description.strip())

    if room.items:
        # Usamos nuestra nueva función para obtener los nombres correctos
        item_names = [get_item_name(item) for item in room.items]
        item_counts = Counter(item_names)
        formatted_items = [f"{name} ({count})" if count > 1 else name for name, count in item_counts.items()]
        items_str = ", ".join(formatted_items)
        parts.append(f"\n<b>Ves aquí:</b> {items_str}.")

    if room.exits_from:
        exits_list = sorted([exit_obj.name.capitalize() for exit_obj in room.exits_from])
        exits_str = ", ".join(exits_list)
        parts.append(f"\n<b>Salidas:</b> [ {exits_str} ]")
    else:
        parts.append("\n<b>Salidas:</b> [ Ninguna ]")

    description_body = "\n".join(parts)
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
            # Esta es una salvaguarda. En un juego normal, no debería ocurrir
            # si el personaje se crea correctamente con una room_id.
            await message.answer("Parece que estás perdido en el vacío. Te hemos llevado a un lugar seguro.")
            # En el futuro, podríamos tener una función para mover al jugador a la sala de inicio.
            return

        room = account.character.room
        # Usamos nuestro formateador para construir el texto de la sala
        formatted_room = await format_room(room)

        # ¡IMPORTANTE! Usamos parse_mode="HTML" para que Telegram entienda las etiquetas <pre> y <b>
        await message.answer(formatted_room, parse_mode="HTML")