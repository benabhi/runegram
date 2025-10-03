# src/services/pulse_service.py
"""
Módulo de Servicio para el Sistema de Pulse Global.

Este servicio implementa un "heartbeat" global que ejecuta un tick cada X segundos
(configurable, por defecto 2 segundos). Todos los sistemas basados en tiempo se
sincronizan con este pulse, lo que permite:

1. Escalabilidad: Un solo job en lugar de cientos por entidad.
2. Sincronización: Todos los sistemas operan con el mismo timing.
3. Simplicidad: Razonamiento sobre tiempo en "ticks" en lugar de cron expressions.
4. Predictibilidad: Orden de ejecución determinista.

Responsabilidades:
- Mantener un contador global de ticks.
- Ejecutar un pulse cada X segundos usando APScheduler.
- Procesar todas las entidades con tick_scripts en cada pulse.
- Determinar qué scripts deben ejecutarse en el tick actual.
- Manejar scripts permanentes (se repiten) y one-shot (se ejecutan una vez).
- Filtrar ejecución por estado online de jugadores (para scripts ambient).
"""

import logging
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from src.config import settings
from src.db import async_session_factory
from src.services import script_service, online_service, player_service
from src.models import Item, Character


# ==============================================================================
# CONFIGURACIÓN GLOBAL
# ==============================================================================

# Intervalo del pulse en segundos (configurable)
PULSE_INTERVAL_SECONDS = 2

# Contador global de ticks (persiste en memoria durante la ejecución del bot)
_global_tick_counter = 0

# Instancia única del scheduler
scheduler = AsyncIOScheduler()


# ==============================================================================
# FUNCIONES PÚBLICAS - INICIALIZACIÓN
# ==============================================================================

def initialize_pulse_system():
    """
    Configura y arranca el sistema de pulse global.
    Debe llamarse al iniciar el bot.
    """
    # Configurar el scheduler con persistencia en BD
    jobstores = {'default': SQLAlchemyJobStore(url=settings.sync_database_url)}
    scheduler.configure(jobstores=jobstores)

    # Programar el pulse global
    scheduler.add_job(
        _execute_global_pulse,
        trigger='interval',
        seconds=PULSE_INTERVAL_SECONDS,
        id='global_pulse',
        replace_existing=True
    )

    scheduler.start()
    logging.info(f"⏰ Pulse System iniciado. Tick cada {PULSE_INTERVAL_SECONDS}s.")


def shutdown_pulse_system():
    """
    Detiene el sistema de pulse de forma ordenada.
    Debe llamarse al apagar el bot.
    """
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logging.info("⏰ Pulse System detenido.")


def get_current_tick() -> int:
    """
    Retorna el contador global de ticks actual.

    Útil para debugging o para que otros sistemas consulten el tick actual.
    """
    return _global_tick_counter


# ==============================================================================
# FUNCIONES PRIVADAS - LÓGICA DEL PULSE
# ==============================================================================

async def _execute_global_pulse():
    """
    Función principal del pulse que se ejecuta cada X segundos.

    Incrementa el contador global y procesa todos los tick_scripts
    de todas las entidades.
    """
    global _global_tick_counter
    _global_tick_counter += 1

    current_tick = _global_tick_counter

    # Log cada 30 ticks (60 segundos con tick=2s) para no saturar logs
    if current_tick % 30 == 0:
        logging.debug(f"⏰ Global Pulse: Tick #{current_tick}")

    async with async_session_factory() as session:
        try:
            # Procesar tick_scripts de Items
            await _process_items_tick_scripts(session, current_tick)

            # Futuro: Procesar tick_scripts de Rooms, Characters, etc.
            # await _process_rooms_tick_scripts(session, current_tick)

        except Exception:
            logging.exception(f"Error crítico en Global Pulse (tick #{current_tick})")


async def _process_items_tick_scripts(session: AsyncSession, current_tick: int):
    """
    Procesa los tick_scripts de todos los Items en la base de datos.

    Args:
        session: Sesión de base de datos activa.
        current_tick: El número de tick actual.
    """
    # Obtener todos los Items con eager loading de relaciones
    query = (
        select(Item)
        .options(
            selectinload(Item.room),
            selectinload(Item.character).selectinload(Character.room)
        )
    )
    result = await session.execute(query)
    all_items = result.scalars().all()

    for item in all_items:
        # Obtener tick_scripts del prototipo
        tick_scripts = item.prototype.get("tick_scripts", [])

        if not tick_scripts:
            continue

        # Inicializar tick_data si no existe
        if item.tick_data is None:
            item.tick_data = {}

        # Procesar cada tick_script del item
        for idx, tick_script in enumerate(tick_scripts):
            await _process_single_tick_script(
                session=session,
                item=item,
                tick_script=tick_script,
                script_index=idx,
                current_tick=current_tick
            )

        # Persistir cambios en tick_data
        await session.commit()


async def _process_single_tick_script(
    session: AsyncSession,
    item: Item,
    tick_script: dict,
    script_index: int,
    current_tick: int
):
    """
    Procesa un tick_script individual de un item.

    Args:
        session: Sesión de base de datos.
        item: El item que tiene el tick_script.
        tick_script: Diccionario con la definición del script.
        script_index: Índice del script en la lista (para tracking).
        current_tick: Tick global actual.
    """
    interval_ticks = tick_script.get("interval_ticks")
    script_string = tick_script.get("script")
    category = tick_script.get("category", "ambient")
    is_permanent = tick_script.get("permanent", True)

    if not interval_ticks or not script_string:
        return

    # Clave para tracking en tick_data
    tracking_key = f"script_{script_index}"

    # Obtener datos de tracking
    script_tracking = item.tick_data.get(tracking_key, {})
    last_executed_tick = script_tracking.get("last_executed_tick", 0)
    has_executed = script_tracking.get("has_executed", False)

    # Si es one-shot y ya se ejecutó, saltar
    if not is_permanent and has_executed:
        return

    # Verificar si debe ejecutarse en este tick
    ticks_since_last = current_tick - last_executed_tick

    if ticks_since_last < interval_ticks:
        return  # Aún no es momento de ejecutar

    # Determinar la sala de contexto
    room = None
    if item.room:
        room = item.room
    elif item.character and item.character.room:
        room = item.character.room

    if not room:
        return  # No hay contexto de sala

    # Obtener personajes en la sala
    char_ids_query = select(Character.id).where(Character.room_id == room.id)
    result = await session.execute(char_ids_query)
    char_ids_in_room = result.scalars().all()

    # Ejecutar el script para cada personaje en la sala (con filtros)
    for char_id in char_ids_in_room:
        # Filtro de online para scripts ambient
        if category == "ambient":
            is_online = await online_service.is_character_online(char_id)
            if not is_online:
                continue

        # Cargar personaje con relaciones
        character = await player_service.get_character_with_relations_by_id(session, char_id)
        if not character:
            continue

        # Ejecutar el script
        context = {
            "target": item,
            "room": character.room,
            "character": character
        }

        await script_service.execute_script(
            script_string=script_string,
            session=session,
            **context
        )

    # Actualizar tracking
    item.tick_data[tracking_key] = {
        "last_executed_tick": current_tick,
        "has_executed": True
    }

    # Marcar como modificado para que SQLAlchemy detecte el cambio en JSONB
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(item, "tick_data")
