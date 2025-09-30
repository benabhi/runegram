# src/services/command_service.py
import logging
from aiogram.types import BotCommand, BotCommandScopeChat
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.bot import bot
from src.models import Character

# Importamos el dispatcher de forma segura para evitar importaciones circulares
def get_command_sets():
    from src.handlers.player.dispatcher import COMMAND_SETS
    return COMMAND_SETS

async def get_active_command_sets_for_character(character: Character) -> list[str]:
    """
    Construye la lista de nombres de CommandSets activos para un personaje.
    """
    if not character:
        return ["character_creation"]

    # --- LÍNEA CORREGIDA ---
    # character.command_sets es una lista, no un diccionario. La tratamos como tal.
    active_sets = set(character.command_sets)

    # 2. Añadimos sets otorgados por los objetos en el inventario.
    for item in character.items:
        granted_sets = item.prototype.get("grants_command_sets", [])
        active_sets.update(granted_sets)

    # 3. Añadimos sets otorgados por la sala actual.
    if hasattr(character.room, 'key') and character.room.key: # Salvaguarda por si la sala no tiene prototipo
        from game_data.room_prototypes import ROOM_PROTOTYPES
        room_proto = ROOM_PROTOTYPES.get(character.room.key, {})
        granted_sets = room_proto.get("grants_command_sets", [])
        active_sets.update(granted_sets)

    # 4. Añadimos sets de administrador si corresponde.
    if character.account and character.account.role == "ADMINISTRADOR":
        active_sets.update(["spawning", "admin_movement", "admin_info"])

    return sorted(list(active_sets))


async def update_telegram_commands(character: Character):
    """
    Actualiza la lista de comandos visibles en el cliente de Telegram
    para un personaje específico.
    """
    if not character:
        return

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

    try:
        scope = BotCommandScopeChat(chat_id=character.account.telegram_id)
        await bot.set_my_commands(commands=telegram_commands, scope=scope)
        logging.info(f"Actualizados {len(telegram_commands)} comandos de Telegram para {character.name}.")
    except Exception as e:
        logging.warning(f"No se pudieron actualizar los comandos de Telegram para {character.name}: {e}")