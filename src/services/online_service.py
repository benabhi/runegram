# src/services/online_service.py
"""
Módulo de Servicio para el Seguimiento de Actividad (Presencia).

Este servicio gestiona el estado de "online" o "AFK" (Away From Keyboard) de los
personajes. Utiliza Redis para un almacenamiento y recuperación de datos de alta
velocidad, lo cual es ideal para datos volátiles como el timestamp de la última
actividad.

Responsabilidades:
- Registrar la última vez que un jugador envía un comando.
- Determinar si un jugador está "online" basándose en un umbral de inactividad.
- Gestionar las notificaciones cuando un jugador pasa a estado AFK o vuelve.
- Proveer una tarea global (`check_for_newly_afk_players`) para ser ejecutada
  periódicamente por el `ticker_service`.
"""

import time
import logging
import redis.asyncio as redis
from datetime import timedelta

from src.config import settings
from src.models import Character
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db import async_session_factory


# --- Configuración del Servicio ---
ONLINE_THRESHOLD = timedelta(minutes=5)

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True
)

# Variable global en memoria para rastrear quién estaba online en el último chequeo.
PREVIOUSLY_ONLINE_IDS = set()


# --- Funciones de Ayuda (Internas) ---

def _get_last_seen_key(character_id: int) -> str:
    """Genera la clave de Redis estandarizada para el timestamp de un personaje."""
    return f"last_seen:{character_id}"

def _get_afk_notified_key(character_id: int) -> str:
    """Genera la clave de Redis para el flag que indica si ya se notificó el estado AFK."""
    return f"afk_notified:{character_id}"


# --- Funciones Principales del Servicio ---

async def update_last_seen(session: AsyncSession, character: Character):
    """
    Actualiza la última actividad de un personaje y notifica si vuelve de estar AFK.
    Esta función es llamada por el dispatcher en cada mensaje.
    """
    from src.services import channel_service

    char_id = character.id

    # 1. Actualizar el timestamp de "última vez visto" en Redis.
    key = _get_last_seen_key(char_id)
    await redis_client.set(key, time.time())
    await redis_client.expire(key, timedelta(days=7))

    # 2. Comprobar si el personaje estaba marcado como AFK.
    afk_notified_key = _get_afk_notified_key(char_id)
    # Usamos `getdel` para obtener y borrar la clave atómicamente si existe.
    was_afk = await redis_client.getdel(afk_notified_key)

    if was_afk:
        # El personaje estaba AFK y acaba de volver. Notificamos.
        logging.info(f"Personaje {character.name} ha vuelto de su inactividad (AFK).")
        await channel_service.broadcast_to_channel(
            session,
            "sistema",
            f"<i>{character.name} ha vuelto de su inactividad.</i>"
        )


async def is_character_online(character_id: int) -> bool:
    """
    Verifica si un personaje se considera "online" (activo recientemente).
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
    """
    Devuelve una lista de todos los objetos Character que se consideran "online".
    """
    result = await session.execute(select(Character))
    all_characters = result.scalars().all()

    online_characters = []
    for char in all_characters:
        if await is_character_online(char.id):
            online_characters.append(char)

    return online_characters

async def check_for_newly_afk_players():
    """
    Tarea global periódica para detectar y notificar sobre personajes que se
    han vuelto inactivos (AFK).
    """
    from src.services import channel_service, player_service
    global PREVIOUSLY_ONLINE_IDS
    logging.info("[AFK CHECK] Ejecutando chequeo de jugadores inactivos...")

    async with async_session_factory() as session:
        try:
            result = await session.execute(select(Character.id))
            all_char_ids = set(result.scalars().all())

            currently_online_ids = set()
            for char_id in all_char_ids:
                if await is_character_online(char_id):
                    currently_online_ids.add(char_id)

            newly_afk_ids = PREVIOUSLY_ONLINE_IDS - currently_online_ids

            for char_id in newly_afk_ids:
                afk_notified_key = _get_afk_notified_key(char_id)
                # Solo notificamos si no lo hemos hecho ya.
                if not await redis_client.exists(afk_notified_key):
                    character = await player_service.get_character_with_relations_by_id(session, char_id)
                    if character:
                        logging.info(f"Personaje {character.name} ha entrado en inactividad (AFK).")
                        await channel_service.broadcast_to_channel(
                            session,
                            "sistema",
                            f"<i>{character.name} ha entrado en inactividad.</i>"
                        )
                        # Marcamos que ya fue notificado para no spamear.
                        await redis_client.set(afk_notified_key, "1", ex=timedelta(days=1))
        except Exception:
            logging.exception("[AFK CHECK] Ocurrió un error durante el chequeo de AFK.")

    PREVIOUSLY_ONLINE_IDS = currently_online_ids
    logging.info(f"[AFK CHECK] Chequeo finalizado. {len(PREVIOUSLY_ONLINE_IDS)} jugadores online.")