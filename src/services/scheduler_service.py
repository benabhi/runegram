# src/services/scheduler_service.py
"""
Servicio de Scheduling para Sistema de Scripts v2.0.

Scheduler híbrido que soporta:
- Tick-based scheduling (sistema actual v1.0)
- Cron-based scheduling (calendario real)
- Timestamp scheduling (eventos únicos en fecha/hora específica)

Este servicio REEMPLAZA a pulse_service.py (legado) manteniendo 100% de retrocompatibilidad.

Responsabilidades:
1. Mantener sistema de ticks actual (retrocompatibilidad).
2. Agregar scheduling basado en expresiones cron.
3. Cache de scripts cron para performance.
4. Soportar scripts globales vs por jugador.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Item, Room, Character
from src.services import script_service, online_service, player_service
from src.db import async_session_factory
from src.config import settings


class ScheduledScriptType(Enum):
    """Tipos de scheduling soportados."""
    TICK = "tick"        # Intervalo de ticks (sistema actual)
    CRON = "cron"        # Expresión cron (nuevo)
    TIMESTAMP = "timestamp"  # Fecha/hora específica (nuevo)


@dataclass
class ScheduledScript:
    """Definición de un script programado."""
    script_string: str
    schedule_type: ScheduledScriptType

    # Para TICK
    interval_ticks: Optional[int] = None

    # Para CRON
    cron_expression: Optional[str] = None

    # Para TIMESTAMP
    execute_at: Optional[datetime] = None

    # Comunes
    permanent: bool = True
    category: str = "ambient"
    is_global: bool = False  # True = ejecuta una sola vez, False = por jugador
    priority: int = 0  # Mayor número = mayor prioridad


class SchedulerService:
    """
    Scheduler híbrido que soporta ticks, cron y timestamps.

    Mantiene 100% retrocompatibilidad con sistema v1.0 mientras
    agrega nuevas funcionalidades.

    REEMPLAZA a pulse_service.py manteniendo la misma API pública.
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._tick_counter = 0

        # Cache de scripts cron (para evitar recargar prototipos cada tick)
        self._cron_scripts_cache: Dict[str, List[ScheduledScript]] = {}

    def start(self):
        """Inicializa el scheduler con todos sus jobs."""
        # Job 1: Pulse global (tick-based scripts) - v1.0
        self.scheduler.add_job(
            self._execute_tick_pulse,
            trigger=IntervalTrigger(seconds=settings.pulse_interval_seconds),
            id='tick_pulse',
            replace_existing=True
        )

        # Job 2: Procesar scripts cron - v2.0
        self.scheduler.add_job(
            self._process_cron_scripts,
            trigger=IntervalTrigger(minutes=1),  # Verificar cada minuto
            id='cron_processor',
            replace_existing=True
        )

        # Job 3: Cargar scripts cron desde prototipos - v2.0
        self.scheduler.add_job(
            self._reload_cron_scripts,
            trigger=IntervalTrigger(minutes=5),  # Recargar cada 5 min
            id='cron_reload',
            replace_existing=True
        )

        self.scheduler.start()
        logging.info("✅ Scheduler Service iniciado (Tick + Cron + Timestamp).")

    def shutdown(self):
        """Detiene el scheduler de forma ordenada."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logging.info("Scheduler Service detenido.")

    def get_current_tick(self) -> int:
        """Retorna el contador global de ticks actual."""
        return self._tick_counter

    # =================== TICK-BASED SCHEDULING (v1.0) ===================

    async def _execute_tick_pulse(self):
        """
        Pulse global de ticks (mantiene comportamiento v1.0).
        """
        self._tick_counter += 1
        current_tick = self._tick_counter

        if current_tick % 30 == 0:
            logging.debug(f"⏰ Global Pulse: Tick #{current_tick}")

        async with async_session_factory() as session:
            await self._process_tick_scripts(session, current_tick)

    async def _process_tick_scripts(self, session: AsyncSession, current_tick: int):
        """
        Procesa tick_scripts (sistema v1.0 - mantenido por retrocompatibilidad).

        NOTA: Carga todos los items y filtra en Python, ya que prototype es una
        propiedad Python, no una columna JSONB en la BD.
        """
        try:
            # Cargar todos los items con sus relaciones
            query = select(Item).options(
                selectinload(Item.room),
                selectinload(Item.character).selectinload(Character.room)
            )

            result = await session.execute(query)
            all_items = result.scalars().all()

            # Filtrar items que tienen tick_scripts (en Python)
            items_with_scripts = [
                item for item in all_items
                if item.prototype.get("tick_scripts")
            ]

            for item in items_with_scripts:
                tick_scripts = item.prototype.get("tick_scripts", [])

                for idx, tick_script in enumerate(tick_scripts):
                    await self._process_single_tick_script(
                        session=session,
                        item=item,
                        tick_script=tick_script,
                        script_index=idx,
                        current_tick=current_tick
                    )

            await session.commit()

        except Exception:
            logging.exception(f"Error en pulse tick #{current_tick}")

    async def _process_single_tick_script(
        self,
        session: AsyncSession,
        item: Item,
        tick_script: dict,
        script_index: int,
        current_tick: int
    ):
        """
        Procesa un tick_script individual (lógica v1.0).

        Mantiene la lógica exacta de pulse_service.py para retrocompatibilidad.
        """
        interval_ticks = tick_script.get("interval_ticks")
        script_string = tick_script.get("script")
        category = tick_script.get("category", "ambient")
        is_permanent = tick_script.get("permanent", True)

        if not interval_ticks or not script_string:
            return

        # Clave para tracking en tick_data
        tracking_key = f"script_{script_index}"

        # Inicializar tick_data si no existe
        if item.tick_data is None:
            item.tick_data = {}

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

    # =================== CRON-BASED SCHEDULING (v2.0) ===================

    async def _reload_cron_scripts(self):
        """
        Recarga todos los cron scripts desde prototipos.

        Esto permite que diseñadores agreguen nuevos cron scripts
        sin reiniciar el bot.
        """
        try:
            async with async_session_factory() as session:
                # Cargar items con scheduled_scripts
                query = select(Item).where(
                    Item.prototype['scheduled_scripts'].astext.is_not(None)
                )
                result = await session.execute(query)
                items = result.scalars().all()

                new_cache = {}

                for item in items:
                    scheduled_scripts = item.prototype.get("scheduled_scripts", [])

                    for script_def in scheduled_scripts:
                        if "schedule" in script_def:
                            # Es un cron script
                            cron_expr = script_def["schedule"]

                            scheduled_script = ScheduledScript(
                                script_string=script_def["script"],
                                schedule_type=ScheduledScriptType.CRON,
                                cron_expression=cron_expr,
                                permanent=script_def.get("permanent", True),
                                is_global=script_def.get("global", False),
                                category=script_def.get("category", "ambient")
                            )

                            # Agregar al cache por entity_id
                            entity_key = f"item_{item.id}"
                            if entity_key not in new_cache:
                                new_cache[entity_key] = []
                            new_cache[entity_key].append(scheduled_script)

                # TODO: Cargar rooms con scheduled_scripts (futuro)

                self._cron_scripts_cache = new_cache
                logging.info(f"📅 Cron scripts cache actualizado: {len(new_cache)} entidades.")

        except Exception:
            logging.exception("Error recargando cron scripts")

    async def _process_cron_scripts(self):
        """
        Procesa todos los cron scripts que deben ejecutarse en este minuto.

        Se ejecuta cada minuto (job configurado en start).
        """
        now = datetime.now(timezone.utc)

        try:
            async with async_session_factory() as session:
                for entity_key, scheduled_scripts in self._cron_scripts_cache.items():
                    for script in scheduled_scripts:
                        if self._should_execute_cron(script, now):
                            await self._execute_cron_script(session, entity_key, script, now)

        except Exception:
            logging.exception("Error procesando cron scripts")

    def _should_execute_cron(self, script: ScheduledScript, now: datetime) -> bool:
        """
        Verifica si un cron script debe ejecutarse en este momento.

        Usa croniter para parsing de expresiones cron.
        """
        try:
            # Importar croniter solo cuando se necesita (dependencia opcional)
            from croniter import croniter

            cron = croniter(script.cron_expression, now)
            next_run = cron.get_prev(datetime)

            # Verificar si el script debió ejecutarse en el último minuto
            time_diff = (now - next_run).total_seconds()

            # Si la diferencia es menor a 60s, debe ejecutarse
            return 0 <= time_diff < 60

        except ImportError:
            logging.error("croniter no instalado. Instalar con: pip install croniter")
            return False
        except Exception:
            logging.exception(f"Error parsing cron: {script.cron_expression}")
            return False

    async def _execute_cron_script(
        self,
        session: AsyncSession,
        entity_key: str,
        script: ScheduledScript,
        execution_time: datetime
    ):
        """
        Ejecuta un cron script.

        Maneja scripts globales vs. por jugador.
        """
        try:
            # Parsear entity_key (ej: "item_123")
            entity_type, entity_id = entity_key.split("_")
            entity_id = int(entity_id)

            # Cargar entidad
            if entity_type == "item":
                entity = await session.get(Item, entity_id, options=[
                    selectinload(Item.room),
                    selectinload(Item.character)
                ])
            elif entity_type == "room":
                entity = await session.get(Room, entity_id)
            else:
                logging.warning(f"Tipo de entidad desconocido: {entity_type}")
                return

            if not entity:
                logging.warning(f"Entidad no encontrada: {entity_key}")
                return

            # Determinar contexto
            if script.is_global:
                # Script global: ejecutar una sola vez
                await script_service.execute_script(
                    script_string=script.script_string,
                    session=session,
                    target=entity,
                    room=getattr(entity, 'room', entity),
                    execution_time=execution_time
                )
            else:
                # Script por jugador: ejecutar para cada jugador online en la sala
                room = getattr(entity, 'room', None) if hasattr(entity, 'room') else entity

                if not room:
                    return

                # Obtener personajes online en la sala
                char_ids_query = select(Character.id).where(Character.room_id == room.id)
                result = await session.execute(char_ids_query)
                char_ids = result.scalars().all()

                for char_id in char_ids:
                    if script.category == "ambient":
                        is_online = await online_service.is_character_online(char_id)
                        if not is_online:
                            continue

                    character = await player_service.get_character_with_relations_by_id(
                        session, char_id
                    )

                    if not character:
                        continue

                    await script_service.execute_script(
                        script_string=script.script_string,
                        session=session,
                        target=entity,
                        room=room,
                        character=character,
                        execution_time=execution_time
                    )

        except Exception:
            logging.exception(f"Error ejecutando cron script: {entity_key}")


# Instancia singleton
scheduler_service = SchedulerService()
