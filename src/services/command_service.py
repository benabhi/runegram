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
    Obtiene el diccionario `COMMAND_SETS` del dispatcher de forma segura para
    evitar importaciones circulares.
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

    # 1. Empezamos con los sets base del personaje desde la BD.
    active_sets = set(character.command_sets)

    # 1.1. Añadimos el set "listing" que está disponible para todos.
    active_sets.add("listing")

    # 2. Añadimos sets otorgados por los objetos en el inventario.
    for item in character.items:
        granted_sets = item.prototype.get("grants_command_sets", [])
        active_sets.update(granted_sets)

    # 3. Añadimos sets otorgados por la sala actual.
    if character.room and character.room.prototype:
        granted_sets = character.room.prototype.get("grants_command_sets", [])
        active_sets.update(granted_sets)

    # 4. Añadimos sets de administrador si el rol de la cuenta es el adecuado.
    if character.account and character.account.role in ["ADMIN", "SUPERADMIN"]:
        active_sets.update(["spawning", "admin_movement", "admin_info", "diagnostics", "management"])

    return sorted(list(active_sets))


async def update_telegram_commands(character: Character = None, account = None):
    """
    Actualiza la lista de comandos visibles en el menú '/' del cliente de Telegram
    para un personaje específico.

    Args:
        character: Personaje para el cual actualizar comandos (opcional)
        account: Cuenta de usuario (requerida si character es None)
    """
    # Si no hay character, usar account directamente para obtener telegram_id
    if not character and not account:
        return

    # Determinar telegram_id y nombre para logs
    if character:
        telegram_id = character.account.telegram_id
        log_name = character.name
        account_obj = character.account
    else:
        telegram_id = account.telegram_id
        log_name = f"cuenta {telegram_id}"
        account_obj = account

    try:
        COMMAND_SETS = get_command_sets()

        # Si hay personaje, obtener sus command sets activos
        # Si no hay personaje, solo mostrar comando de creación
        if character:
            active_set_names = await get_active_command_sets_for_character(character)
        else:
            # Sin personaje, solo mostrar comandos de creación de personaje
            active_set_names = ["character_creation"]

        telegram_commands = []
        seen_commands = set()

        # Construimos la lista de objetos BotCommand que la API de Telegram espera.
        for set_name in active_set_names:
            for command_instance in COMMAND_SETS.get(set_name, []):
                main_name = command_instance.names[0]
                if main_name not in seen_commands:
                    telegram_commands.append(
                        BotCommand(command=main_name, description=command_instance.description)
                    )
                    seen_commands.add(main_name)

        # Usamos un `BotCommandScopeChat` para aplicar estos comandos únicamente
        # al chat con este jugador específico.
        scope = BotCommandScopeChat(chat_id=telegram_id)
        await bot.set_my_commands(commands=telegram_commands, scope=scope)

        logging.info(f"Actualizados {len(telegram_commands)} comandos de Telegram para {log_name}.")

    except Exception as e:
        # Los errores al actualizar comandos no son críticos y no deben detener el juego.
        logging.warning(f"No se pudieron actualizar los comandos de Telegram para {log_name}: {e}")