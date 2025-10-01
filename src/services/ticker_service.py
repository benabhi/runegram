# src/services/ticker_service.py
"""
Módulo de Servicio para Tareas Programadas (Tickers).

Este servicio es el "corazón" que hace que el mundo de Runegram se sienta vivo.
Utiliza la librería APScheduler para ejecutar scripts de forma periódica,
independientemente de las acciones de los jugadores.

Responsabilidades:
- Inicializar y configurar el scheduler global (APScheduler).
- Cargar las definiciones de tickers desde los prototipos de `game_data`.
- Programar, ejecutar y gestionar el ciclo de vida de estas tareas.
- Determinar el contexto correcto para un ticker (ej: la sala de un objeto)
  y filtrar su ejecución (ej: solo para jugadores activos).
"""

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

# Instancia única del scheduler para toda la aplicación.
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
    necesarias para evitar errores de carga perezosa.
    """
    MODEL_MAP = {"Item": Item, "Room": Room, "Character": Character}
    model_class = MODEL_MAP.get(entity_type)
    if not model_class:
        logging.warning(f"ADVERTENCIA: Tipo de entidad desconocido '{entity_type}' para ticker.")
        return None

    query = select(model_class)
    if model_class is Item:
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
# SECCIÓN DE INICIALIZACIÓN Y CARGA
# ==============================================================================

def initialize_scheduler():
    """Configura y arranca el scheduler global. Debe llamarse al iniciar el bot."""
    jobstores = {'default': SQLAlchemyJobStore(url=settings.sync_database_url)}
    scheduler.configure(jobstores=jobstores)
    scheduler.start()
    logging.info("⏰ Ticker Service iniciado y listo para programar tareas.")

async def load_and_schedule_all_tickers(session: AsyncSession):
    """
    Busca todas las entidades con tickers en la base de datos (actualmente solo Items)
    y las programa. Debe llamarse una vez al iniciar el bot para asegurar la persistencia.
    """
    logging.info("Cargando y programando tickers para todas las entidades existentes...")
    try:
        result = await session.execute(select(Item))
        all_items = result.scalars().all()
        for item in all_items:
            if item.prototype.get("tickers"):
                logging.info(f"  -> Programando tickers para el item '{item.key}' (ID: {item.id})")
                await schedule_tickers_for_entity(item)
        logging.info("Carga de tickers existentes finalizada.")
    except Exception:
        logging.exception("Error al cargar los tickers de entidades existentes.")


# ==============================================================================
# SECCIÓN DE EJECUCIÓN DE TAREAS
# ==============================================================================

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
    Función que APScheduler llama. Prepara el contexto, comprueba la actividad
    del jugador y delega la ejecución al script_service.
    """
    async with async_session_factory() as session:
        try:
            entity = await get_entity_by_id(session, entity_id, entity_type)
            if not entity: return

            # 1. Determinar la sala de contexto del ticker.
            room = None
            if hasattr(entity, 'room') and entity.room:
                room = entity.room
            elif hasattr(entity, 'character') and entity.character and entity.character.room:
                room = entity.character.room

            if not room: return

            # 2. Encontrar los IDs de los personajes en esa sala.
            char_ids_query = select(Character.id).where(Character.room_id == room.id)
            result = await session.execute(char_ids_query)
            char_ids_in_room = result.scalars().all()

            # 3. Iterar sobre cada personaje, aplicar filtros y ejecutar el script.
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
        except Exception:
            logging.exception(f"Error crítico en la ejecución del ticker para {entity_type} {entity_id}")