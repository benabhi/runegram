# src/services/player_service.py
"""
Módulo de Servicio para la Gestión de Jugadores y Personajes.

Este es uno de los servicios centrales de la aplicación. Encapsula toda la
lógica de negocio para crear, recuperar y modificar las entidades `Account` y
`Character`.

Actúa como la única capa que interactúa directamente con los modelos de jugador,
asegurando que toda la lógica de negocio esté centralizada y sea consistente.
"""

import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.account import Account
from src.models.character import Character
from src.models.room import Room
from src.models.item import Item
from src.models.exit import Exit
from src.services import channel_service, command_service


async def get_character_with_relations_by_id(session: AsyncSession, character_id: int) -> Character | None:
    """
    Busca un personaje por su ID y carga explícitamente todas sus relaciones
    críticas (sala, inventario, cuenta, configuraciones) en una sola consulta.

    Esta es una función de ayuda crucial para evitar errores de "carga perezosa"
    (lazy loading) en un entorno asíncrono.
    """
    try:
        query = (
            select(Character)
            .where(Character.id == character_id)
            .options(
                selectinload(Character.room).selectinload(Room.items).selectinload(Item.contained_items),
                selectinload(Character.room).selectinload(Room.exits_from).selectinload(Exit.to_room),
                selectinload(Character.room).selectinload(Room.characters),
                selectinload(Character.items).selectinload(Item.contained_items),
                selectinload(Character.account),
                selectinload(Character.settings)
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
    except Exception:
        logging.exception(f"Error al obtener el personaje completo con ID {character_id}")
        return None

async def get_or_create_account(session: AsyncSession, telegram_id: int) -> Account:
    """
    Busca una cuenta por su telegram_id. Si no existe, la crea.
    Garantiza que el objeto `Account` devuelto contenga un `Character` completamente
    cargado si este existe.
    """
    try:
        # 1. Buscar la cuenta y su personaje asociado.
        account_query = select(Account).where(Account.telegram_id == telegram_id).options(selectinload(Account.character))
        result = await session.execute(account_query)
        account = result.scalar_one_or_none()

        # 2. Si la cuenta no existe, crearla y devolverla.
        if not account:
            logging.info(f"Creando nueva cuenta para el telegram_id: {telegram_id}")
            new_account = Account(telegram_id=telegram_id)
            session.add(new_account)
            await session.commit()
            # Recargar la cuenta con la relación character explícitamente
            await session.refresh(new_account, ["character"])
            return new_account

        # 3. Si la cuenta existe pero no tiene personaje, devolverla tal cual.
        if not account.character:
            return account

        # 4. Si la cuenta y el personaje existen, usar nuestra función de ayuda para
        #    asegurarnos de que el personaje está completamente cargado con todas sus relaciones.
        full_character = await get_character_with_relations_by_id(session, account.character.id)
        account.character = full_character
        return account
    except Exception:
        logging.exception(f"Error al obtener o crear la cuenta para telegram_id {telegram_id}")
        # En caso de un fallo crítico, es más seguro devolver None.
        return None

async def create_character(session: AsyncSession, telegram_id: int, character_name: str) -> Character:
    """
    Crea un nuevo personaje, lo asocia a una cuenta, y dispara los hooks de bienvenida.
    """
    account = await get_or_create_account(session, telegram_id)
    if not account:
        raise RuntimeError("No se pudo obtener o crear una cuenta de usuario.")

    # Validaciones de negocio
    if account.character is not None:
        raise ValueError("Ya tienes un personaje asociado a esta cuenta.")

    result = await session.execute(select(Character).where(Character.name == character_name))
    if result.scalar_one_or_none():
        raise ValueError(f"El nombre '{character_name}' ya está en uso. Por favor, elige otro.")

    # Creación y persistencia
    new_character = Character(
        name=character_name,
        account_id=account.id,
        room_id=1 # Asigna a la sala de inicio "limbo"
    )
    session.add(new_character)
    await session.commit()

    # Recargamos el personaje por completo para tener todas las relaciones disponibles.
    full_character = await get_character_with_relations_by_id(session, new_character.id)
    if not full_character:
        raise RuntimeError("No se pudo recargar el personaje recién creado.")

    # Hooks de post-creación
    await channel_service.get_or_create_settings(session, full_character)
    welcome_message = (
        f"¡Bienvenido al mundo, {full_character.name}! "
        "Usa los comandos de movimiento como <b>/norte</b> o <b>/sur</b> para explorar. "
        "Si necesitas ayuda, puedes preguntar en este canal usando <b>/novato [tu pregunta]</b>. "
        "Para una lista de comandos más detallada, escribe <b>/ayuda</b>."
    )
    await channel_service.broadcast_to_channel(session, "novato", welcome_message)

    await command_service.update_telegram_commands(full_character)

    return full_character


async def teleport_character(session: AsyncSession, character_id: int, to_room_id: int):
    """Mueve un personaje a una nueva sala actualizando su `room_id`."""
    # Validación: asegurar que la sala de destino existe.
    result = await session.execute(select(Room).where(Room.id == to_room_id))
    if not result.scalar_one_or_none():
        raise ValueError(f"La sala con ID {to_room_id} no existe.")

    # Actualización atómica
    query = update(Character).where(Character.id == character_id).values(room_id=to_room_id)
    await session.execute(query)
    await session.commit()