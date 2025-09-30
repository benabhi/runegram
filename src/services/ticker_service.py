# src/services/ticker_service.py
import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.db import async_session_factory
from src.services import script_service, online_service, player_service
from src.models import Item, Room, Character

scheduler = AsyncIOScheduler()


# ==============================================================================
# SECCIÓN DE FUNCIONES AUXILIARES
# ==============================================================================

def parse_schedule(schedule_str: str) -> tuple[str, dict]:
    """
    Parsea el string de schedule del prototipo y lo convierte en argumentos para APScheduler.
    """
    if schedule_str.startswith("interval:"):
        seconds = int(schedule_str.split(':')[1])
        return 'interval', {'seconds': seconds}
    if schedule_str.startswith("date:"):
        date_val = schedule_str.split(':', 1)[1]
        return 'date', {'run_date': date_val}
    cron_expr = schedule_str
    if schedule_str.startswith("cron:"):
        cron_expr = schedule_str.split(':', 1)[1]
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        logging.warning(f"ADVERTENCIA: Expresión cron mal formada en '{schedule_str}'. Se ignora.")
        return 'cron', {}
    cron_args = { 'minute': parts[0], 'hour': parts[1], 'day': parts[2], 'month': parts[3], 'day_of_week': parts[4] }
    return 'cron', cron_args


async def get_entity_by_id(session: AsyncSession, entity_id: int, entity_type: str):
    """
    Busca una entidad por su ID y tipo, cargando explícitamente las relaciones
    necesarias para evitar errores de carga perezosa (lazy loading).
    """
    MODEL_MAP = {"Item": Item, "Room": Room, "Character": Character}
    model_class = MODEL_MAP.get(entity_type)
    if not model_class:
        logging.warning(f"ADVERTENCIA: Tipo de entidad desconocido '{entity_type}' para ticker.")
        return None

    query = select(model_class)

    # --- CAMBIO CLAVE: Carga de relaciones anidadas ---
    if model_class is Item:
        # Si es un Item, necesitamos precargar:
        # 1. La sala en la que está (si está en una).
        # 2. El personaje que lo lleva (si lo lleva alguien).
        # 3. La sala del personaje que lo lleva.
        query = query.options(
            selectinload(Item.room),
            selectinload(Item.character).selectinload(Character.room)
        )
    elif model_class is Character:
        query = query.options(selectinload(Character.room), selectinload(Character.account))

    query = query.where(model_class.id == entity_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


# ==============================================================================
# SECCIÓN PRINCIPAL DEL SERVICIO
# ==============================================================================

def initialize_scheduler():
    """Configura y arranca el scheduler global."""
    jobstores = {'default': SQLAlchemyJobStore(url=settings.sync_database_url)}
    scheduler.configure(jobstores=jobstores)
    scheduler.start()
    logging.info("⏰ Ticker Service iniciado y listo para programar tareas.")

async def load_and_schedule_all_tickers(session: AsyncSession):
    """
    Busca todas las entidades con tickers en la base de datos y las programa.
    """
    logging.info("Cargando y programando tickers para todas las entidades existentes...")
    result = await session.execute(select(Item))
    all_items = result.scalars().all()
    for item in all_items:
        if item.prototype.get("tickers"):
            logging.info(f"  -> Programando tickers para el item '{item.key}' (ID: {item.id})")
            await schedule_tickers_for_entity(item)
    logging.info("Carga de tickers existentes finalizada.")

async def schedule_tickers_for_entity(entity):
    """
    Lee los tickers del prototipo de una entidad y los añade al scheduler.
    """
    prototype_tickers = entity.prototype.get("tickers", [])
    for ticker_data in prototype_tickers:
        schedule_str = ticker_data.get("schedule")
        script_str = ticker_data.get("script")
        category = ticker_data.get("category", "ambient")
        if not schedule_str or not script_str:
            continue
        trigger_type, trigger_args = parse_schedule(schedule_str)
        if not trigger_args:
            continue
        job_id = f"ticker_{type(entity).__name__}_{entity.id}_{schedule_str}_{script_str}"
        scheduler.add_job(
            execute_ticker_script, trigger=trigger_type,
            args=[entity.id, type(entity).__name__, script_str, category],
            id=job_id, replace_existing=True, **trigger_args
        )

async def execute_ticker_script(entity_id: int, entity_type: str, script_string: str, category: str):
    """
    Función que APScheduler llama. Ahora es inteligente y encuentra la sala
    incluso si el objeto está en el inventario de un personaje.
    """
    async with async_session_factory() as session:
        entity = await get_entity_by_id(session, entity_id, entity_type)
        if not entity:
            return

        # --- CAMBIO CLAVE: Lógica para encontrar la sala ---
        room = None
        if hasattr(entity, 'room') and entity.room:
            # Opción 1: El objeto está en una sala.
            room = entity.room
        elif hasattr(entity, 'character') and entity.character and entity.character.room:
            # Opción 2: El objeto lo lleva un personaje, usamos la sala de ese personaje.
            room = entity.character.room

        if not room:
            # Si no hay sala por ninguno de los dos métodos, abortamos.
            return

        char_ids_in_room_query = select(Character.id).where(Character.room_id == room.id)
        result = await session.execute(char_ids_in_room_query)
        char_ids_in_room = result.scalars().all()

        for char_id in char_ids_in_room:
            is_online = await online_service.is_character_online(char_id)
            if category == "ambient" and not is_online:
                continue

            full_character = await player_service.get_character_with_relations_by_id(session, char_id)
            if not full_character:
                continue

            context = {
                "target": entity,
                "room": full_character.room,
                "character": full_character
            }

            await script_service.execute_script(
                script_string=script_string,
                session=session,
                **context
            )