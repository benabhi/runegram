# src/services/channel_service.py
"""
Módulo de Servicio para la Gestión de Canales de Chat.

Este servicio encapsula toda la lógica de negocio relacionada con los canales
de comunicación globales. Sus responsabilidades incluyen:
- Gestionar la configuración de canales por personaje (suscripciones).
- Formatear y transmitir mensajes a todos los jugadores suscritos a un canal.
- Proveer funciones de ayuda para comprobar el estado de los canales.

Depende de `broadcaster_service` para el envío final de mensajes y de
`game_data/channel_prototypes.py` como fuente de la verdad sobre los
canales disponibles.
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Character, CharacterSetting
from src.services import broadcaster_service
from game_data.channel_prototypes import CHANNEL_PROTOTYPES

async def get_or_create_settings(session: AsyncSession, character: Character) -> CharacterSetting:
    """
    Obtiene las configuraciones para un personaje. Si no existen, las crea con
    los valores por defecto definidos en los prototipos de canal.

    Los canales se activan por defecto si:
    1. Tienen default_on=True, O
    2. Tienen audience configurado Y el personaje tiene permisos para acceder

    Args:
        session (AsyncSession): La sesión de base de datos activa.
        character (Character): El personaje para el que se obtienen las configuraciones.

    Returns:
        CharacterSetting: El objeto de configuración del personaje.
    """
    # Si las settings ya están cargadas en el objeto character, las devolvemos directamente.
    if character.settings:
        return character.settings

    # Si no, las creamos.
    logging.info(f"Creando configuraciones por defecto para el personaje {character.name}")

    # Determinar qué canales deben estar activados por defecto.
    default_channels = []

    from src.services import permission_service

    for key, data in CHANNEL_PROTOTYPES.items():
        # Activar si tiene default_on=True
        if data.get("default_on", False):
            default_channels.append(key)
            continue

        # Activar si tiene audience Y el personaje tiene permisos
        audience_filter = data.get("audience", "")
        if audience_filter:
            can_access, _ = await permission_service.can_execute(character, audience_filter)
            if can_access:
                default_channels.append(key)
                logging.info(f"Canal '{key}' activado por defecto para {character.name} (tiene permisos de audience)")

    new_settings = CharacterSetting(
        character_id=character.id,
        active_channels={"active_channels": default_channels}
    )
    session.add(new_settings)
    await session.commit()

    # Refrescamos el objeto 'character' para que la relación 'settings' se cargue.
    await session.refresh(character, attribute_names=["settings"])

    return character.settings

async def is_channel_active(settings: CharacterSetting, channel_key: str) -> bool:
    """Comprueba si un canal está en la lista de canales activos de un jugador."""
    if not settings:
        return False
    return channel_key in settings.active_channels.get("active_channels", [])

async def broadcast_to_channel(session: AsyncSession, channel_key: str, message: str, exclude_character_id: int | None = None):
    """
    Envía un mensaje a todos los jugadores que estén suscritos a un canal
    y que cumplan con los requisitos de audiencia.
    """
    try:
        if channel_key not in CHANNEL_PROTOTYPES:
            logging.warning(f"Intento de transmitir a un canal desconocido: {channel_key}")
            return

        # 1. Formatear el mensaje con el ícono y nombre del canal.
        proto = CHANNEL_PROTOTYPES[channel_key]
        formatted_message = f"{proto['icon']} <b>{proto['name']}:</b> {message}"

        # 2. Obtener filtro de audiencia (si existe).
        audience_filter = proto.get("audience", "")

        # 3. Obtener todos los personajes del juego.
        #    Precargamos sus settings y cuentas para evitar consultas adicionales en el bucle.
        query = select(Character).options(selectinload(Character.settings), selectinload(Character.account))
        result = await session.execute(query)
        all_characters = result.scalars().all()

        # 4. Iterar y enviar el mensaje a los que estén suscritos y cumplan con audiencia.
        for char in all_characters:
            if char.id == exclude_character_id:
                continue

            settings = await get_or_create_settings(session, char)
            if not await is_channel_active(settings, channel_key):
                continue

            # Validar permiso de audiencia si existe filtro.
            if audience_filter:
                from src.services import permission_service
                can_receive, _ = await permission_service.can_execute(char, audience_filter)
                if not can_receive:
                    logging.debug(
                        f"Saltando mensaje de canal '{channel_key}' a {char.name}: "
                        "no cumple filtro de audiencia"
                    )
                    continue

            await broadcaster_service.send_message_to_character(char, formatted_message)
    except Exception:
        logging.exception(f"Error al transmitir al canal '{channel_key}'")

async def set_channel_status(session: AsyncSession, character: Character, channel_key: str, activate: bool):
    """
    Activa o desactiva un canal para un personaje.

    Al activar, valida que el personaje tenga permiso según el filtro de audiencia del canal.
    """
    if channel_key not in CHANNEL_PROTOTYPES:
        raise ValueError("El canal especificado no existe.")

    proto = CHANNEL_PROTOTYPES[channel_key]
    settings = await get_or_create_settings(session, character)

    # Validar permiso de audiencia al activar.
    if activate:
        audience_filter = proto.get("audience", "")
        if audience_filter:
            from src.services import permission_service
            can_subscribe, error_msg = await permission_service.can_execute(
                character,
                audience_filter
            )
            if not can_subscribe:
                raise ValueError(
                    f"No tienes permiso para suscribirte al canal '{proto['name']}'. "
                    "Este canal está restringido a ciertos jugadores."
                )

    # SQLAlchemy es capaz de detectar cambios en listas dentro de un JSONB "mutable".
    # Obtenemos la lista actual de canales activos.
    active_channels_list = settings.active_channels.get("active_channels", [])

    if activate:
        # Añadir el canal si no está ya en la lista.
        if channel_key not in active_channels_list:
            active_channels_list.append(channel_key)
    else: # Desactivar
        # Quitar el canal si está en la lista.
        if channel_key in active_channels_list:
            active_channels_list.remove(channel_key)

    # Reasignamos la lista modificada al campo JSONB.
    settings.active_channels["active_channels"] = active_channels_list

    # Marcamos el objeto como "modificado" para que SQLAlchemy sepa que debe guardarlo.
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(settings, "active_channels")

    await session.commit()