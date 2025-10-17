# src/services/__init__.py
"""
Módulo de Servicios del Motor de Runegram.

Este archivo centraliza las exportaciones de todos los servicios disponibles
para facilitar su importación desde otros módulos del proyecto.
"""

# Servicios Core
from src.services.player_service import (
    get_or_create_account,
    create_character,
    get_character_by_account_and_name,
    get_all_characters_by_account,
    delete_character,
    get_character_with_relations_by_id,
    get_character_with_items_by_id
)

from src.services.command_service import get_available_commands
from src.services.permission_service import permission_service
from src.services.broadcaster_service import broadcaster_service
from src.services.online_service import online_service
from src.services.narrative_service import narrative_service
from src.services.script_service import script_service
from src.services.validation_service import validation_service
from src.services.channel_service import channel_service
from src.services.ban_service import ban_service
from src.services.world_service import world_service
from src.services.world_loader_service import world_loader_service
from src.services.item_service import item_service
from src.services.tag_service import tag_service

# Servicios de Scripts v2.0
from src.services.event_service import event_service, EventType, EventPhase, EventContext, EventResult
from src.services.scheduler_service import scheduler_service
from src.services.state_service import state_service

__all__ = [
    # Player Service
    "get_or_create_account",
    "create_character",
    "get_character_by_account_and_name",
    "get_all_characters_by_account",
    "delete_character",
    "get_character_with_relations_by_id",
    "get_character_with_items_by_id",

    # Command Service
    "get_available_commands",

    # Singleton Services
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
    "EventType",
    "EventPhase",
    "EventContext",
    "EventResult",
    "scheduler_service",
    "state_service",
]
