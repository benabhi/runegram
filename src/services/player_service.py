# src/services/player_service.py

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.account import Account
from src.models.character import Character
from src.models.room import Room
from src.models.item import Item
from src.models.exit import Exit


async def get_or_create_account(session: AsyncSession, telegram_id: int) -> Account:
    """
    Busca una cuenta por su telegram_id. Si no existe, la crea.
    Devuelve el objeto de la cuenta con sus relaciones ya cargadas.
    """
    # --- LÓGICA SIMPLIFICADA Y CORREGIDA ---

    # 1. Intentamos encontrar la cuenta
    # Definimos la estrategia de carga aquí para aplicarla si encontramos la cuenta.
    load_strategy = select(Account).options(
        selectinload(Account.character).selectinload(Character.room).selectinload(Room.items),
        selectinload(Account.character).selectinload(Character.room).selectinload(Room.exits_from),
        selectinload(Account.character).selectinload(Character.items)
    )
    query = load_strategy.where(Account.telegram_id == telegram_id)
    result = await session.execute(query)
    account = result.scalar_one_or_none()

    # 2. Si la cuenta existe, la devolvemos. Viene con todo precargado.
    if account:
        return account

    # 3. Si no existe, la creamos y la devolvemos.
    # El objeto devuelto estará "fresco" y sus relaciones (como .character)
    # serán None por defecto, lo cual es el estado correcto para una nueva cuenta.
    print(f"Creando nueva cuenta para el telegram_id: {telegram_id}")
    new_account = Account(telegram_id=telegram_id)
    session.add(new_account)
    await session.commit()
    await session.refresh(new_account) # Usamos refresh para obtener el ID y roles por defecto

    return new_account


async def create_character(session: AsyncSession, telegram_id: int, character_name: str) -> Character:
    """
    Crea un nuevo personaje y lo asocia a una cuenta existente.
    Lanza una excepción si la cuenta no existe, ya tiene un personaje,
    o el nombre del personaje ya está en uso.
    """
    # 1. Buscamos la cuenta.
    account = await get_or_create_account(session, telegram_id)

    # 2. Verificamos que la cuenta no tenga ya un personaje
    if account.character is not None:
        raise ValueError("Ya tienes un personaje asociado a esta cuenta.")

    # 3. Verificamos que el nombre no esté en uso
    result = await session.execute(select(Character).where(Character.name == character_name))
    if result.scalar_one_or_none():
        raise ValueError(f"El nombre '{character_name}' ya está en uso. Por favor, elige otro.")

    # 4. Creamos el nuevo personaje
    new_character = Character(
        name=character_name,
        account_id=account.id,
        room_id=1
    )
    session.add(new_character)
    await session.commit()

    # 5. Expiramos la instancia de 'account' para forzar una recarga completa
    # la próxima vez que se necesite, asegurando que la relación .character se actualice.
    session.expire(account)

    await session.refresh(new_character)
    return new_character


async def teleport_character(session: AsyncSession, character_id: int, to_room_id: int):
    """Mueve un personaje a una nueva sala."""
    # Verificamos que la sala de destino exista
    result = await session.execute(select(Room).where(Room.id == to_room_id))
    if not result.scalar_one_or_none():
        raise ValueError(f"La sala con ID {to_room_id} no existe.")

    # Actualizamos la room_id del personaje
    query = update(Character).where(Character.id == character_id).values(room_id=to_room_id)
    await session.execute(query)
    await session.commit()