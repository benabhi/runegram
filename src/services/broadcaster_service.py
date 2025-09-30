# src/services/broadcaster_service.py

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
    """
    if not character:
        logging.warning("BROADCASTER: Se intentó enviar un mensaje a un personaje nulo.")
        return

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
        # Usamos logging.exception para obtener un traceback completo si el envío falla
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
    """
    if not room_id:
        logging.warning("BROADCASTER: Se intentó enviar un mensaje a un room_id nulo.")
        return

    query = (
        select(Character)
        .where(Character.room_id == room_id)
        .options(selectinload(Character.account))
    )

    result = await session.execute(query)
    characters_in_room = result.scalars().all()

    for char in characters_in_room:
        if char.id == exclude_character_id:
            continue

        await send_message_to_character(
            character=char,
            message_text=message_text,
            parse_mode=parse_mode
        )