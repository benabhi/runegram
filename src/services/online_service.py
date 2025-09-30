# src/services/online_service.py
import time
import logging
import redis.asyncio as redis
from datetime import timedelta

from src.config import settings
from src.models import Character
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db import async_session_factory # Importamos la fábrica de sesiones

# --- CONFIGURACIÓN ---
ONLINE_THRESHOLD = timedelta(minutes=5)

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True
)

def _get_last_seen_key(character_id: int) -> str:
    return f"last_seen:{character_id}"

def _get_afk_notified_key(character_id: int) -> str:
    return f"afk_notified:{character_id}"

PREVIOUSLY_ONLINE_IDS = set()

async def update_last_seen(session: AsyncSession, character: Character):
    """
    Actualiza la última actividad y notifica si el personaje vuelve de estar AFK.
    """
    from src.services import channel_service
    char_id = character.id
    key = _get_last_seen_key(char_id)
    await redis_client.set(key, time.time())
    await redis_client.expire(key, timedelta(days=7))

    afk_notified_key = _get_afk_notified_key(char_id)
    if await redis_client.exists(afk_notified_key):
        logging.info(f"Personaje {character.name} ha vuelto de su inactividad (AFK).")
        await channel_service.broadcast_to_channel(
            session,
            "sistema",
            f"<i>{character.name} ha vuelto de su inactividad.</i>"
        )
        await redis_client.delete(afk_notified_key)

async def is_character_online(character_id: int) -> bool:
    """
    Verifica si un personaje se considera "online" basado en su última actividad.
    """
    key = _get_last_seen_key(character_id)
    last_seen_timestamp_str = await redis_client.get(key)
    if not last_seen_timestamp_str:
        return False
    try:
        elapsed_time = time.time() - float(last_seen_timestamp_str)
        return elapsed_time < ONLINE_THRESHOLD.total_seconds()
    except (ValueError, TypeError):
        return False

async def get_online_characters(session: AsyncSession) -> list[Character]:
    # ... (código sin cambios) ...
    result = await session.execute(select(Character))
    all_characters = result.scalars().all()
    online_characters = []
    for char in all_characters:
        if await is_character_online(char.id):
            online_characters.append(char)
    return online_characters

# --- FUNCIÓN MODIFICADA ---
async def check_for_newly_afk_players():
    """
    Una tarea global que detecta personajes que acaban de pasar a estado AFK y los notifica.
    Esta función ahora crea su propia sesión de base de datos.
    """
    from src.services import channel_service, player_service
    global PREVIOUSLY_ONLINE_IDS
    logging.info("[AFK CHECK] Ejecutando chequeo de jugadores inactivos...")

    # Creamos una sesión de corta duración solo para esta tarea
    async with async_session_factory() as session:
        result = await session.execute(select(Character.id))
        all_char_ids = set(result.scalars().all())

        currently_online_ids = set()
        for char_id in all_char_ids:
            if await is_character_online(char_id):
                currently_online_ids.add(char_id)

        newly_afk_ids = PREVIOUSLY_ONLINE_IDS - currently_online_ids

        for char_id in newly_afk_ids:
            afk_notified_key = _get_afk_notified_key(char_id)
            if not await redis_client.exists(afk_notified_key):
                character = await player_service.get_character_with_relations_by_id(session, char_id)
                if character:
                    logging.info(f"Personaje {character.name} ha entrado en inactividad (AFK).")
                    await channel_service.broadcast_to_channel(
                        session,
                        "sistema",
                        f"<i>{character.name} ha entrado en inactividad.</i>"
                    )
                    await redis_client.set(afk_notified_key, "1", ex=timedelta(days=1))

    PREVIOUSLY_ONLINE_IDS = currently_online_ids
    logging.info(f"[AFK CHECK] Chequeo finalizado. {len(PREVIOUSLY_ONLINE_IDS)} jugadores online.")