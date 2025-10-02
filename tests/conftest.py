# tests/conftest.py
"""
Configuración Global de Pytest y Fixtures Compartidas.

Este archivo define fixtures y configuración que estarán disponibles para todos
los tests del proyecto.
"""

import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from src.models.base import Base
from src.models import Account, Character, Room, Exit, Item, CharacterSetting
from game_data.room_prototypes import ROOM_PROTOTYPES


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture que proporciona una sesión de base de datos temporal para tests.

    Crea una base de datos en memoria (SQLite) para cada test, lo que garantiza:
    - Aislamiento completo entre tests
    - Velocidad (en memoria)
    - No contamina la base de datos de desarrollo/producción

    Uso:
        async def test_algo(db_session):
            account = Account(telegram_id=12345)
            db_session.add(account)
            await db_session.commit()
    """
    # Crear un motor de BD en memoria para el test
    # IMPORTANTE: Usar StaticPool en lugar de NullPool para SQLite in-memory
    # para asegurar que todas las operaciones usan la misma conexión
    from sqlalchemy.pool import StaticPool

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Cambiar a True para ver queries SQL en los tests
    )

    # Crear todas las tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Crear la sesión
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_factory() as session:
        yield session

    # Cleanup
    await engine.dispose()


@pytest.fixture
async def sample_room(db_session: AsyncSession) -> Room:
    """
    Fixture que crea una sala de ejemplo para tests.

    Returns:
        Room: Una sala básica con key "test_room"
    """
    room = Room(
        key="test_room",
        name="Sala de Test",
        description="Una sala de prueba para los tests."
    )
    db_session.add(room)
    await db_session.commit()
    await db_session.refresh(room)
    return room


@pytest.fixture
async def sample_account(db_session: AsyncSession) -> Account:
    """
    Fixture que crea una cuenta de ejemplo para tests.

    Returns:
        Account: Una cuenta básica con telegram_id 999999
    """
    account = Account(telegram_id=999999, role="PLAYER")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def sample_character(db_session: AsyncSession, sample_account: Account, sample_room: Room) -> Character:
    """
    Fixture que crea un personaje de ejemplo para tests.

    Requiere:
        - sample_account: Fixture de cuenta
        - sample_room: Fixture de sala

    Returns:
        Character: Un personaje básico asociado a la cuenta y sala de prueba
    """
    character = Character(
        name="TestCharacter",
        account_id=sample_account.id,
        room_id=sample_room.id
    )
    db_session.add(character)
    await db_session.commit()
    await db_session.refresh(character)
    return character


@pytest.fixture
async def admin_account(db_session: AsyncSession) -> Account:
    """
    Fixture que crea una cuenta de administrador para tests.

    Returns:
        Account: Una cuenta con rol ADMIN
    """
    account = Account(telegram_id=888888, role="ADMIN")
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def admin_character(db_session: AsyncSession, admin_account: Account, sample_room: Room) -> Character:
    """
    Fixture que crea un personaje administrador para tests.

    Returns:
        Character: Un personaje con permisos de administrador
    """
    character = Character(
        name="AdminCharacter",
        account_id=admin_account.id,
        room_id=sample_room.id
    )
    db_session.add(character)
    await db_session.commit()
    await db_session.refresh(character)
    return character


@pytest.fixture
async def sample_item(db_session: AsyncSession, sample_room: Room) -> Item:
    """
    Fixture que crea un item de ejemplo en una sala.

    Returns:
        Item: Un item básico con key "test_item"
    """
    item = Item(
        key="test_item",
        room_id=sample_room.id
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item


# Marks personalizados para categorizar tests
def pytest_configure(config):
    """
    Registra marks personalizados para pytest.

    Uso:
        @pytest.mark.critical
        def test_important_feature():
            pass
    """
    config.addinivalue_line(
        "markers", "critical: marca tests críticos que deben pasar siempre"
    )
    config.addinivalue_line(
        "markers", "slow: marca tests que tardan más de 1 segundo"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración (requieren múltiples componentes)"
    )
