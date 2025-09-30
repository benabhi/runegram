# src/services/online_service.py
import time
import redis.asyncio as redis
from datetime import timedelta

from src.config import settings
from src.models import Character
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


# --- CONFIGURACIÓN ---
# Si un jugador no ha enviado un comando en este tiempo, se considera "offline".
ONLINE_THRESHOLD = timedelta(minutes=5)

# Creamos un cliente de Redis dedicado para este servicio.
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True  # Importante para que devuelva strings, no bytes
)

def _get_redis_key(character_id: int) -> str:
    """Genera la clave de Redis estandarizada para un personaje."""
    return f"last_seen:{character_id}"

async def update_last_seen(character_id: int):
    """
    Actualiza el timestamp de la última actividad de un personaje a "ahora".
    """
    key = _get_redis_key(character_id)
    # Guardamos el timestamp actual como un número flotante (ej: 1678886400.0)
    await redis_client.set(key, time.time())
    # Opcional: Hacemos que la clave expire después de un tiempo para no llenar Redis.
    # Una semana es un tiempo razonable.
    await redis_client.expire(key, timedelta(days=7))

async def is_character_online(character_id: int) -> bool:
    """
    Verifica si un personaje se considera "online" basado en su última actividad.
    """
    key = _get_redis_key(character_id)
    last_seen_timestamp_str = await redis_client.get(key)

    if not last_seen_timestamp_str:
        return False  # Si no hay registro, no está online.

    try:
        last_seen_timestamp = float(last_seen_timestamp_str)
        # Calculamos el tiempo transcurrido
        elapsed_time = time.time() - last_seen_timestamp
        # Comparamos con nuestro umbral
        return elapsed_time < ONLINE_THRESHOLD.total_seconds()
    except (ValueError, TypeError):
        return False

async def get_online_characters(session: AsyncSession) -> list[Character]:
    """
    Devuelve una lista de todos los personajes que se consideran "online".
    """
    result = await session.execute(select(Character))
    all_characters = result.scalars().all()

    online_characters = []
    for char in all_characters:
        if await is_character_online(char.id):
            online_characters.append(char)

    return online_characters