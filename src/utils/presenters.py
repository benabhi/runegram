# src/utils/presenters.py

from aiogram import types

from src.models.room import Room
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

    # --- Secciones futuras (fácil de añadir más aquí) ---

    # Futuro: Añadir la lista de objetos en el suelo
    # if room.items:
    #     items_str = ", ".join([item.name for item in room.items])
    #     parts.append(f"\n<b>Ves aquí:</b> {items_str}")

    # Futuro: Añadir la lista de otros jugadores en la sala
    # if other_players:
    #     players_str = ", ".join([player.name for player in other_players])
    #     parts.append(f"\n<b>También están aquí:</b> {players_str}")

    # 3. Salidas
    if room.exits:
        # Obtenemos las salidas y las capitalizamos para que se vean mejor
        exits_list = [exit_name.capitalize() for exit_name in room.exits.keys()]
        exits_str = ", ".join(exits_list)
        parts.append(f"\n<b>Salidas:</b> [ {exits_str} ]")
    else:
        parts.append("\n<b>Salidas:</b> [ Ninguna ]")

    # Unimos todas las partes con saltos de línea
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