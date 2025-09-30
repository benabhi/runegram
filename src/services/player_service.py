# src/services/player_service.py

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
    críticas para evitar errores de carga perezosa.
    """
    query = (
        select(Character)
        .where(Character.id == character_id)
        .options(
            selectinload(Character.room).selectinload(Room.items),
            selectinload(Character.room).selectinload(Room.exits_from),
            selectinload(Character.items),
            selectinload(Character.account),
            selectinload(Character.settings)
        )
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_or_create_account(session: AsyncSession, telegram_id: int) -> Account:
    """
    Busca una cuenta por su telegram_id. Si no existe, la crea.
    Devuelve el objeto de la cuenta con su personaje y todas las relaciones cargadas.
    """
    # Primero, buscamos la cuenta y su relación con el personaje.
    account_query = select(Account).where(Account.telegram_id == telegram_id).options(selectinload(Account.character))
    result = await session.execute(account_query)
    account = result.scalar_one_or_none()

    # Si la cuenta no existe, la creamos y la devolvemos. No tendrá personaje.
    if not account:
        print(f"Creando nueva cuenta para el telegram_id: {telegram_id}")
        new_account = Account(telegram_id=telegram_id)
        session.add(new_account)
        await session.commit()
        await session.refresh(new_account)
        return new_account

    # Si la cuenta existe pero no tiene personaje, la devolvemos tal cual.
    if not account.character:
        return account

    # Si la cuenta y el personaje existen, recargamos el personaje con todas sus relaciones.
    full_character = await get_character_with_relations_by_id(session, account.character.id)
    account.character = full_character
    return account


async def create_character(session: AsyncSession, telegram_id: int, character_name: str) -> Character:
    """
    Crea un nuevo personaje, lo asocia a una cuenta, y envía un mensaje de bienvenida.
    """
    account = await get_or_create_account(session, telegram_id)

    if account.character is not None:
        raise ValueError("Ya tienes un personaje asociado a esta cuenta.")

    result = await session.execute(select(Character).where(Character.name == character_name))
    if result.scalar_one_or_none():
        raise ValueError(f"El nombre '{character_name}' ya está en uso. Por favor, elige otro.")

    new_character = Character(
        name=character_name,
        account_id=account.id,
        room_id=1 # Asigna a la sala de inicio "limbo"
    )
    session.add(new_character)
    await session.commit() # Al hacer commit, new_character obtiene su ID.

    # --- CAMBIO CLAVE: Recargamos el personaje por completo ---
    # Usamos la función que ya creamos para obtener una versión "fresca" y completa
    # del personaje, con todas sus relaciones cargadas (incluida .account).
    full_character = await get_character_with_relations_by_id(session, new_character.id)

    # Ahora usamos este objeto 'full_character' para el resto de operaciones.
    if not full_character:
        # Esto es una salvaguarda, nunca debería ocurrir.
        raise RuntimeError("No se pudo recargar el personaje recién creado.")

    # --- MENSAJE DE BIENVENIDA ---
    await channel_service.get_or_create_settings(session, full_character)
    welcome_message = (
        f"¡Bienvenido al mundo, {full_character.name}! "
        "Usa los comandos de movimiento como <b>/norte</b> o <b>/sur</b> para explorar. "
        "Si necesitas ayuda, puedes preguntar en este canal usando <b>/novato [tu pregunta]</b>. "
        "Para una lista de comandos más detallada, escribe <b>/ayuda</b>."
    )
    await channel_service.broadcast_to_channel(session, "novato", welcome_message)

    # --- ACTUALIZAR COMANDOS DE TELEGRAM ---
    # Después de crear el personaje, establecemos su lista inicial de comandos.
    await command_service.update_telegram_commands(full_character)

    return full_character


async def teleport_character(session: AsyncSession, character_id: int, to_room_id: int):
    """Mueve un personaje a una nueva sala."""
    result = await session.execute(select(Room).where(Room.id == to_room_id))
    if not result.scalar_one_or_none():
        raise ValueError(f"La sala con ID {to_room_id} no existe.")

    query = update(Character).where(Character.id == character_id).values(room_id=to_room_id)
    await session.execute(query)
    await session.commit()