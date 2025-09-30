# src/services/channel_service.py
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Character, CharacterSetting
from src.services import broadcaster_service, player_service
from game_data.channel_prototypes import CHANNEL_PROTOTYPES

async def get_or_create_settings(session: AsyncSession, character: Character) -> CharacterSetting:
    """Obtiene o crea las configuraciones para un personaje, asegurando valores por defecto."""
    if character.settings:
        return character.settings

    logging.info(f"Creando configuraciones por defecto para el personaje {character.name}")

    # Determinamos los canales activos por defecto desde los prototipos
    default_channels = [
        key for key, data in CHANNEL_PROTOTYPES.items() if data.get("default_on", False)
    ]

    new_settings = CharacterSetting(
        character_id=character.id,
        active_channels={"active_channels": default_channels}
    )
    session.add(new_settings)
    await session.commit()
    await session.refresh(new_settings)
    # Refrescamos también el personaje para que la relación se actualice
    await session.refresh(character, attribute_names=["settings"])

    return new_settings

async def is_channel_active(settings: CharacterSetting, channel_key: str) -> bool:
    """Comprueba si un canal está en la lista de canales activos de un jugador."""
    return channel_key in settings.active_channels.get("active_channels", [])

async def broadcast_to_channel(session: AsyncSession, channel_key: str, message: str, exclude_character_id: int | None = None):
    """
    Envía un mensaje a todos los jugadores suscritos a un canal.
    """
    if channel_key not in CHANNEL_PROTOTYPES:
        logging.warning(f"Intento de transmitir a un canal desconocido: {channel_key}")
        return

    proto = CHANNEL_PROTOTYPES[channel_key]
    formatted_message = f"{proto['icon']} <b>{proto['name']}:</b> {message}"

    # Buscamos a todos los personajes que tengan la configuración
    query = select(Character).options(selectinload(Character.settings), selectinload(Character.account))
    result = await session.execute(query)
    all_characters = result.scalars().all()

    for char in all_characters:
        if char.id == exclude_character_id:
            continue

        # Obtenemos/creamos las settings y comprobamos si el canal está activo para este usuario
        settings = await get_or_create_settings(session, char)
        if await is_channel_active(settings, channel_key):
            await broadcaster_service.send_message_to_character(char, formatted_message)

async def set_channel_status(session: AsyncSession, character: Character, channel_key: str, activate: bool):
    """Activa o desactiva un canal para un personaje."""
    if channel_key not in CHANNEL_PROTOTYPES:
        raise ValueError("El canal especificado no existe.")

    settings = await get_or_create_settings(session, character)
    active_channels_list = settings.active_channels.get("active_channels", [])

    if activate:
        if channel_key not in active_channels_list:
            active_channels_list.append(channel_key)
    else: # Desactivar
        if channel_key in active_channels_list:
            active_channels_list.remove(channel_key)

    # SQLAlchemy detecta el cambio en el JSONB y lo guardará
    settings.active_channels["active_channels"] = active_channels_list
    await session.commit()