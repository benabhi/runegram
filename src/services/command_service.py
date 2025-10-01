# src/services/command_service.py
"""
Módulo de Servicio para la Gestión de Comandos.

Este servicio es el cerebro detrás del sistema de comandos dinámicos.
No define los comandos en sí, sino que orquesta cuáles están disponibles
para un jugador en un momento dado y cómo se presentan en la interfaz.

Responsabilidades Clave:
1. Calcular la lista de `CommandSets` activos para un personaje basándose
   en su estado, equipo y ubicación (contexto).
2. Sincronizar la lista de comandos disponibles con la interfaz del cliente
   de Telegram, proporcionando una experiencia de usuario (UX) reactiva.
"""

import logging
from aiogram.types import BotCommand, BotCommandScopeChat
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.bot import bot
from src.models import Character

def get_command_sets() -> dict:
    """
    Obtiene el diccionario `COMMAND_SETS` del dispatcher de forma segura.
    """
    from src.handlers.player.dispatcher import COMMAND_SETS
    return COMMAND_SETS

async def get_active_command_sets_for_character(character: Character) -> list[str]:
    """
    Construye la lista de nombres de CommandSets activos para un personaje
    basándose en su contexto actual (base, equipo, sala, rol).
    """
    if not character:
        return ["character_creation"]

    active_sets = set(character.command_sets)

    for item in character.items:
        granted_sets = item.prototype.get("grants_command_sets", [])
        active_sets.update(granted_sets)

    if character.room and character.room.prototype:
        granted_sets = character.room.prototype.get("grants_command_sets", [])
        active_sets.update(granted_sets)

    if character.account and character.account.role in ["ADMIN", "SUPERADMIN"]:
        active_sets.update(["spawning", "admin_movement", "admin_info", "diagnostics"])

    return sorted(list(active_sets))


async def update_telegram_commands(character: Character):
    """
    Actualiza la lista de comandos visibles en el menú '/' del cliente de Telegram
    para un personaje específico.
    """
    if not character or not character.account:
        return

    try:
        COMMAND_SETS = get_command_sets()
        active_set_names = await get_active_command_sets_for_character(character)

        telegram_commands = []
        seen_commands = set()

        for set_name in active_set_names:
            for command_instance in COMMAND_SETS.get(set_name, []):
                main_name = command_instance.names[0]
                if main_name not in seen_commands:
                    telegram_commands.append(
                        BotCommand(command=main_name, description=command_instance.description)
                    )
                    seen_commands.add(main_name)

        scope = BotCommandScopeChat(chat_id=character.account.telegram_id)
        await bot.set_my_commands(commands=telegram_commands, scope=scope)

        logging.info(f"Actualizados {len(telegram_commands)} comandos de Telegram para {character.name}.")

    except Exception as e:
        logging.warning(f"No se pudieron actualizar los comandos de Telegram para {character.name}: {e}")