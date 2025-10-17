# src/services/event_service.py
"""
Servicio de Manejo de Eventos para el Sistema de Scripts v2.0.

Este servicio centraliza el manejo de eventos para que los comandos
puedan disparar eventos sin necesidad de conocer qué scripts existen.

Responsabilidades:
1. Gestionar eventos de tipo BEFORE y AFTER para todas las acciones.
2. Ejecutar scripts definidos en prototipos según eventos.
3. Permitir cancelación de acciones mediante scripts BEFORE.
4. Soportar hooks globales para sistemas del motor.
"""

from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass, field
import logging
from sqlalchemy.ext.asyncio import AsyncSession


# Definición de eventos soportados
class EventType(Enum):
    """Tipos de eventos disponibles en el sistema."""

    # Items
    ON_LOOK = "on_look"
    ON_GET = "on_get"
    ON_DROP = "on_drop"
    ON_USE = "on_use"
    ON_OPEN = "on_open"
    ON_CLOSE = "on_close"
    ON_PUT = "on_put"
    ON_TAKE = "on_take"
    ON_DESTROY = "on_destroy"

    # Rooms
    ON_ENTER = "on_enter"
    ON_LEAVE = "on_leave"
    ON_ROOM_LOOK = "on_room_look"

    # Characters
    ON_LOGIN = "on_login"
    ON_LOGOUT = "on_logout"
    ON_DEATH = "on_death"
    ON_RESPAWN = "on_respawn"
    ON_LEVEL_UP = "on_level_up"

    # Combat (futuro)
    ON_ATTACK = "on_attack"
    ON_DEFEND = "on_defend"
    ON_DAMAGE = "on_damage"
    ON_KILL = "on_kill"
    ON_DIE = "on_die"


# Fases de ejecución de eventos
class EventPhase(Enum):
    """Fases de ejecución de eventos."""
    BEFORE = "before"  # Puede cancelar la acción
    AFTER = "after"    # Ejecuta después de la acción


@dataclass
class EventContext:
    """Contexto completo de un evento."""
    session: AsyncSession
    character: Optional[Any] = None  # Character que dispara el evento
    target: Optional[Any] = None      # Entidad objetivo (Item, Room, etc.)
    room: Optional[Any] = None        # Room donde ocurre
    extra: Dict[str, Any] = field(default_factory=dict)  # Datos adicionales


@dataclass
class EventResult:
    """Resultado de ejecutar un evento."""
    success: bool              # ¿El evento se ejecutó correctamente?
    cancel_action: bool = False  # ¿Cancelar la acción original? (solo BEFORE)
    message: Optional[str] = None  # Mensaje opcional para el jugador
    data: Dict[str, Any] = field(default_factory=dict)  # Datos adicionales


class EventHub:
    """
    Hub centralizado para manejo de eventos.

    Permite que los comandos disparen eventos sin conocer
    qué scripts existen.

    Ejemplo de uso:
        context = EventContext(
            session=session,
            character=character,
            target=item,
            room=room
        )

        result = await event_service.trigger_event(
            event_type=EventType.ON_GET,
            phase=EventPhase.BEFORE,
            context=context
        )

        if result.cancel_action:
            await message.answer("La acción fue cancelada.")
            return
    """

    def __init__(self):
        # Hooks globales: funciones que escuchan TODOS los eventos de un tipo
        self._global_hooks: Dict[EventType, List[Callable]] = {}

    async def trigger_event(
        self,
        event_type: EventType,
        phase: EventPhase,
        context: EventContext
    ) -> EventResult:
        """
        Dispara un evento y ejecuta todos los scripts asociados.

        Args:
            event_type: Tipo de evento (ON_GET, ON_LOOK, etc.)
            phase: Fase del evento (BEFORE o AFTER)
            context: Contexto completo del evento

        Returns:
            EventResult con el resultado de la ejecución
        """
        # Construir nombre del evento con fase
        event_name = f"{phase.value}_{event_type.value}"

        # 1. Ejecutar hooks globales (si existen)
        await self._execute_global_hooks(event_type, phase, context)

        # 2. Ejecutar scripts de la entidad objetivo
        if context.target:
            result = await self._execute_entity_scripts(
                entity=context.target,
                event_name=event_name,
                context=context,
                phase=phase
            )

            if phase == EventPhase.BEFORE and result.cancel_action:
                return result

        return EventResult(success=True)

    async def _execute_entity_scripts(
        self,
        entity: Any,
        event_name: str,
        context: EventContext,
        phase: EventPhase
    ) -> EventResult:
        """
        Ejecuta los scripts definidos en el prototipo de una entidad.

        Soporta tanto formato v1.0 (string simple) como v2.0 (lista con prioridades).
        """
        from src.services import script_service

        # Obtener prototipo
        if not hasattr(entity, 'prototype'):
            return EventResult(success=True)

        prototype = entity.prototype
        scripts = prototype.get("scripts", {})

        # Obtener scripts para este evento
        event_scripts = scripts.get(event_name)

        if not event_scripts:
            return EventResult(success=True)

        # Normalizar a lista de scripts
        script_list = self._normalize_scripts(event_scripts, phase)

        # Ejecutar en orden de prioridad
        for script_def in script_list:
            script_string = script_def.get("script")

            if not script_string:
                continue

            try:
                result = await script_service.execute_script(
                    script_string=script_string,
                    session=context.session,
                    character=context.character,
                    target=context.target,
                    room=context.room,
                    **context.extra
                )

                # Si script retorna False en fase BEFORE, cancelar
                if phase == EventPhase.BEFORE and result is False:
                    return EventResult(
                        success=True,
                        cancel_action=True,
                        message=script_def.get("cancel_message", "La acción fue cancelada.")
                    )

            except Exception:
                logging.exception(f"Error ejecutando script de evento {event_name}")

        return EventResult(success=True)

    def _normalize_scripts(self, event_scripts: Any, phase: EventPhase) -> list:
        """
        Normaliza scripts de v1.0 y v2.0 a formato unificado.

        v1.0: "on_look": "script()"
        v2.0: "on_look": [{"script": "script()", "priority": 0, "phase": "after"}]

        Returns:
            Lista normalizada de scripts con prioridad.
        """
        # v1.0: String simple
        if isinstance(event_scripts, str):
            return [{
                "script": event_scripts,
                "priority": 0,
                "phase": phase.value
            }]

        # v2.0: Lista de scripts
        if isinstance(event_scripts, list):
            normalized = []
            for script_def in event_scripts:
                if isinstance(script_def, str):
                    # Lista de strings: ["script1", "script2"]
                    normalized.append({
                        "script": script_def,
                        "priority": 0,
                        "phase": phase.value
                    })
                elif isinstance(script_def, dict):
                    # Ya está en formato v2.0
                    normalized.append({
                        "script": script_def.get("script"),
                        "priority": script_def.get("priority", 0),
                        "phase": script_def.get("phase", "after"),
                        "cancel_message": script_def.get("cancel_message")
                    })

            # Filtrar por fase
            normalized = [
                s for s in normalized
                if s.get("phase", "after") == phase.value
            ]

            # Ordenar por prioridad (mayor primero)
            normalized.sort(key=lambda s: s.get("priority", 0), reverse=True)

            return normalized

        return []

    async def _execute_global_hooks(
        self,
        event_type: EventType,
        phase: EventPhase,
        context: EventContext
    ):
        """Ejecuta hooks globales registrados para este tipo de evento."""
        hooks = self._global_hooks.get(event_type, [])

        for hook_func in hooks:
            try:
                await hook_func(phase, context)
            except Exception:
                logging.exception(f"Error en hook global para {event_type}")

    def register_global_hook(
        self,
        event_type: EventType,
        hook_func: Callable
    ):
        """
        Registra un hook global que escucha todos los eventos de un tipo.

        Útil para sistemas del motor que necesitan reaccionar a eventos
        (ej: sistema de combate, logging, achievements, etc.)

        Args:
            event_type: Tipo de evento a escuchar
            hook_func: Función async a ejecutar cuando ocurra el evento
        """
        if event_type not in self._global_hooks:
            self._global_hooks[event_type] = []

        self._global_hooks[event_type].append(hook_func)
        logging.info(f"Hook global registrado para {event_type.value}")


# Instancia singleton
event_service = EventHub()
