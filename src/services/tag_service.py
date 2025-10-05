# src/services/tag_service.py
"""
Servicio para búsqueda y filtrado por Categories y Tags.

Este servicio permite buscar y filtrar Rooms e Items basándose en:
- Category: Una categoría única por objeto (ej: "ciudad_runegard", "arma")
- Tags: Múltiples etiquetas por objeto (ej: ["exterior", "seguro"], ["espada", "magica"])

Las categories y tags se definen en los prototipos (game_data/) y se acceden
mediante properties en los modelos Room e Item.
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.room import Room
from src.models.item import Item


# --- Búsquedas de Rooms ---

async def find_rooms_by_category(session: AsyncSession, category: str) -> list[Room]:
    """
    Encuentra todas las salas de una categoría específica.

    Args:
        session: Sesión de BD activa
        category: Categoría a buscar (ej: "ciudad_runegard", "bosque_oscuro")

    Returns:
        Lista de objetos Room que pertenecen a la categoría
    """
    result = await session.execute(select(Room))
    all_rooms = result.scalars().all()
    return [room for room in all_rooms if room.category == category]


async def find_rooms_by_tag(session: AsyncSession, tag: str) -> list[Room]:
    """
    Encuentra todas las salas que tienen un tag específico.

    Args:
        session: Sesión de BD activa
        tag: Tag a buscar (ej: "exterior", "peligroso")

    Returns:
        Lista de objetos Room que contienen el tag
    """
    result = await session.execute(select(Room))
    all_rooms = result.scalars().all()
    return [room for room in all_rooms if tag in room.tags]


async def find_rooms_by_tags_all(session: AsyncSession, tags: list[str]) -> list[Room]:
    """
    Encuentra salas que tienen TODOS los tags especificados (AND lógico).

    Args:
        session: Sesión de BD activa
        tags: Lista de tags que deben estar presentes

    Returns:
        Lista de objetos Room que contienen todos los tags
    """
    result = await session.execute(select(Room))
    all_rooms = result.scalars().all()
    return [room for room in all_rooms if all(tag in room.tags for tag in tags)]


async def find_rooms_by_tags_any(session: AsyncSession, tags: list[str]) -> list[Room]:
    """
    Encuentra salas que tienen AL MENOS UNO de los tags especificados (OR lógico).

    Args:
        session: Sesión de BD activa
        tags: Lista de tags de los cuales al menos uno debe estar presente

    Returns:
        Lista de objetos Room que contienen al menos un tag
    """
    result = await session.execute(select(Room))
    all_rooms = result.scalars().all()
    return [room for room in all_rooms if any(tag in room.tags for tag in tags)]


# --- Búsquedas de Items ---

async def find_items_by_category(session: AsyncSession, category: str) -> list[Item]:
    """
    Encuentra todos los items de una categoría específica.

    Args:
        session: Sesión de BD activa
        category: Categoría a buscar (ej: "arma", "contenedor", "consumible")

    Returns:
        Lista de objetos Item que pertenecen a la categoría
    """
    result = await session.execute(select(Item))
    all_items = result.scalars().all()
    return [item for item in all_items if item.category == category]


async def find_items_by_tag(session: AsyncSession, tag: str) -> list[Item]:
    """
    Encuentra todos los items que tienen un tag específico.

    Args:
        session: Sesión de BD activa
        tag: Tag a buscar (ej: "magica", "unica")

    Returns:
        Lista de objetos Item que contienen el tag
    """
    result = await session.execute(select(Item))
    all_items = result.scalars().all()
    return [item for item in all_items if tag in item.tags]


async def find_items_by_tags_all(session: AsyncSession, tags: list[str]) -> list[Item]:
    """
    Encuentra items que tienen TODOS los tags especificados (AND lógico).

    Args:
        session: Sesión de BD activa
        tags: Lista de tags que deben estar presentes

    Returns:
        Lista de objetos Item que contienen todos los tags
    """
    result = await session.execute(select(Item))
    all_items = result.scalars().all()
    return [item for item in all_items if all(tag in item.tags for tag in tags)]


async def find_items_by_tags_any(session: AsyncSession, tags: list[str]) -> list[Item]:
    """
    Encuentra items que tienen AL MENOS UNO de los tags especificados (OR lógico).

    Args:
        session: Sesión de BD activa
        tags: Lista de tags de los cuales al menos uno debe estar presente

    Returns:
        Lista de objetos Item que contienen al menos un tag
    """
    result = await session.execute(select(Item))
    all_items = result.scalars().all()
    return [item for item in all_items if any(tag in item.tags for tag in tags)]


# --- Funciones de utilidad ---

def get_all_categories_from_rooms() -> set[str]:
    """
    Retorna todas las categorías únicas de salas desde los prototipos.

    Returns:
        Set de categorías únicas (strings)
    """
    from game_data.room_prototypes import ROOM_PROTOTYPES

    categories = set()
    for proto in ROOM_PROTOTYPES.values():
        if cat := proto.get("category"):
            categories.add(cat)
    return categories


def get_all_tags_from_rooms() -> set[str]:
    """
    Retorna todos los tags únicos de salas desde los prototipos.

    Returns:
        Set de tags únicos (strings)
    """
    from game_data.room_prototypes import ROOM_PROTOTYPES

    tags = set()
    for proto in ROOM_PROTOTYPES.values():
        tags.update(proto.get("tags", []))
    return tags


def get_all_categories_from_items() -> set[str]:
    """
    Retorna todas las categorías únicas de items desde los prototipos.

    Returns:
        Set de categorías únicas (strings)
    """
    from game_data.item_prototypes import ITEM_PROTOTYPES

    categories = set()
    for proto in ITEM_PROTOTYPES.values():
        if cat := proto.get("category"):
            categories.add(cat)
    return categories


def get_all_tags_from_items() -> set[str]:
    """
    Retorna todos los tags únicos de items desde los prototipos.

    Returns:
        Set de tags únicos (strings)
    """
    from game_data.item_prototypes import ITEM_PROTOTYPES

    tags = set()
    for proto in ITEM_PROTOTYPES.values():
        tags.update(proto.get("tags", []))
    return tags
