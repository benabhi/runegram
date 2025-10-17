# src/services/__init__.py
"""
Módulo de Servicios del Motor de Runegram.

Este archivo centraliza las exportaciones de todos los servicios disponibles
para facilitar su importación desde otros módulos del proyecto.
"""

# Importar módulos de servicios completos
from src.services import player_service
from src.services import command_service
from src.services import permission_service
from src.services import broadcaster_service
from src.services import online_service
from src.services import narrative_service
from src.services import script_service
from src.services import validation_service
from src.services import channel_service
from src.services import ban_service
from src.services import world_service
from src.services import world_loader_service
from src.services import item_service
from src.services import tag_service

# Scripts v2.0 Services - importar singletons directamente
from src.services.event_service import event_service, EventType, EventPhase, EventContext, EventResult
from src.services.scheduler_service import scheduler_service
from src.services.state_service import state_service

__all__ = [
    # Service Modules
    "player_service",
    "command_service",
    "permission_service",
    "broadcaster_service",
    "online_service",
    "narrative_service",
    "script_service",
    "validation_service",
    "channel_service",
    "ban_service",
    "world_service",
    "world_loader_service",
    "item_service",
    "tag_service",

    # Scripts v2.0 Services
    "event_service",
    "scheduler_service",
    "state_service",

    # Event System Types
    "EventType",
    "EventPhase",
    "EventContext",
    "EventResult",
]
