# src/services/broadcaster_service.py
"""
Módulo de Servicio de Transmisión (Broadcasting).

Este archivo centraliza toda la lógica para enviar mensajes a los jugadores
a través del bot de Telegram. Actúa como una capa de abstracción sobre la API
directa del bot.

Centralizar la comunicación aquí ofrece varias ventajas:
1.  **Consistencia:** Todos los mensajes enviados por el juego pueden tener un
    formato y comportamiento consistentes.
2.  **Manejo de Errores Unificado:** La lógica para manejar errores de la API de
    Telegram (ej: un usuario bloquea el bot) se encuentra en un solo lugar.
3.  **Desacoplamiento:** El resto de los servicios (scripts, canales, etc.) no
    necesitan saber los detalles de cómo se envía un mensaje; simplemente
    llaman a una función en este servicio.
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.bot.bot import bot
from src.models import Character


async def send_message_to_character(
    character: Character,
    message_text: str,
    parse_mode: str = "HTML"
):
    """
    Envía un mensaje formateado a un personaje específico.

    Args:
        character (Character): La instancia del modelo Character a la que se enviará el mensaje.
                               Es crucial que este objeto tenga su relación `.account` precargada.
        message_text (str): El contenido del mensaje a enviar.
        parse_mode (str): El modo de parseo de Telegram (por defecto 'HTML').
    """
    if not character:
        logging.warning("BROADCASTER: Se intentó enviar un mensaje a un personaje nulo.")
        return

    # Salvaguarda para asegurar que la relación con la cuenta está cargada.
    if not character.account:
        logging.error(f"BROADCASTER: El personaje {character.name} (ID: {character.id}) no tiene su cuenta cargada. No se puede enviar mensaje.")
        return

    try:
        logging.info(f"[BROADCASTER DEBUG] Intentando enviar mensaje a {character.name} (Chat ID: {character.account.telegram_id})")
        await bot.send_message(
            chat_id=character.account.telegram_id,
            text=message_text,
            parse_mode=parse_mode
        )
        logging.info(f"[BROADCASTER DEBUG] Mensaje enviado con éxito a {character.name}")
    except Exception:
        # Usamos logging.exception para obtener un traceback completo si el envío falla.
        # Esto es común si un usuario ha bloqueado el bot. No debe detener el juego.
        logging.exception(f"BROADCASTER: No se pudo enviar mensaje a {character.name} (ID: {character.id})")


async def send_message_to_room(
    session: AsyncSession,
    room_id: int,
    message_text: str,
    exclude_character_id: int | None = None,
    parse_mode: str = "HTML"
):
    """
    Envía un mensaje a todos los personajes presentes en una sala específica.

    Args:
        session (AsyncSession): La sesión de base de datos activa.
        room_id (int): El ID de la sala a la que se enviará el mensaje.
        message_text (str): El contenido del mensaje a enviar.
        exclude_character_id (int, optional): El ID de un personaje a excluir de la transmisión.
        parse_mode (str): El modo de parseo de Telegram.
    """
    if not room_id:
        logging.warning("BROADCASTER: Se intentó enviar un mensaje a un room_id nulo.")
        return

    # 1. Obtenemos todos los personajes en la sala.
    #    Usamos `selectinload(Character.account)` para cargar eficientemente la
    #    información de la cuenta de todos los personajes en una sola consulta.
    query = (
        select(Character)
        .where(Character.room_id == room_id)
        .options(selectinload(Character.account))
    )
    result = await session.execute(query)
    characters_in_room = result.scalars().all()

    # 2. Iteramos y enviamos el mensaje a cada personaje.
    for char in characters_in_room:
        if char.id == exclude_character_id:
            continue

        # Reutilizamos nuestra propia función para mantener la lógica de envío en un solo lugar.
        await send_message_to_character(
            character=char,
            message_text=message_text,
            parse_mode=parse_mode
        )