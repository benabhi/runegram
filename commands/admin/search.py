# commands/admin/search.py
"""
Comandos de Administración para Búsqueda por Categories y Tags.

Estos comandos permiten a los administradores buscar y filtrar
Rooms e Items usando el sistema de categories y tags.
"""

import logging
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character, Room, Item
from src.services import tag_service


class CmdListRooms(Command):
    """Lista salas filtradas por category o tags."""
    names = ["listar_rooms", "list_rooms"]
    lock = "role:ADMIN"
    description = "Lista salas. Uso: /listar_rooms [category:X] [tag:Y]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            if not args:
                # Listar todas
                result = await session.execute(select(Room))
                rooms = result.scalars().all()
            else:
                # Parsear filtros
                category_filter = None
                tag_filters = []

                for arg in args:
                    if arg.startswith("category:"):
                        category_filter = arg.split(":", 1)[1]
                    elif arg.startswith("tag:"):
                        tag_filters.append(arg.split(":", 1)[1])

                # Ejecutar búsqueda
                if category_filter:
                    rooms = await tag_service.find_rooms_by_category(session, category_filter)
                elif tag_filters:
                    rooms = await tag_service.find_rooms_by_tags_all(session, tag_filters)
                else:
                    result = await session.execute(select(Room))
                    rooms = result.scalars().all()

            # Formatear resultado
            output = f"🔍 <b>Salas encontradas ({len(rooms)}):</b>\n\n"

            if not rooms:
                output += "No se encontraron salas con esos criterios."
            else:
                for room in rooms[:20]:  # Límite de 20
                    category_str = f" [cat: {room.category}]" if room.category else ""
                    tags_str = f" [tags: {', '.join(room.tags)}]" if room.tags else ""
                    output += f"• <b>{room.name}</b> (ID: {room.id}){category_str}{tags_str}\n"

                if len(rooms) > 20:
                    output += f"\n... y {len(rooms) - 20} más."

            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Error al listar salas.")
            logging.exception(f"Error en /listar_rooms para {character.name}")


class CmdListItems(Command):
    """Lista items filtrados por category o tags."""
    names = ["listar_items", "list_items"]
    lock = "role:ADMIN"
    description = "Lista items. Uso: /listar_items [category:X] [tag:Y]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            if not args:
                # Listar todos
                result = await session.execute(select(Item))
                items = result.scalars().all()
            else:
                # Parsear filtros
                category_filter = None
                tag_filters = []

                for arg in args:
                    if arg.startswith("category:"):
                        category_filter = arg.split(":", 1)[1]
                    elif arg.startswith("tag:"):
                        tag_filters.append(arg.split(":", 1)[1])

                # Ejecutar búsqueda
                if category_filter:
                    items = await tag_service.find_items_by_category(session, category_filter)
                elif tag_filters:
                    items = await tag_service.find_items_by_tags_all(session, tag_filters)
                else:
                    result = await session.execute(select(Item))
                    items = result.scalars().all()

            # Formatear resultado
            output = f"🔍 <b>Items encontrados ({len(items)}):</b>\n\n"

            if not items:
                output += "No se encontraron items con esos criterios."
            else:
                for item in items[:20]:  # Límite de 20
                    category_str = f" [cat: {item.category}]" if item.category else ""
                    tags_str = f" [tags: {', '.join(item.tags)}]" if item.tags else ""
                    location = "inventario" if item.character_id else f"sala {item.room_id}" if item.room_id else "contenedor"
                    output += f"• <b>{item.get_name()}</b> (ID: {item.id}) - {location}{category_str}{tags_str}\n"

                if len(items) > 20:
                    output += f"\n... y {len(items) - 20} más."

            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Error al listar items.")
            logging.exception(f"Error en /listar_items para {character.name}")


class CmdShowCategories(Command):
    """Muestra todas las categorías disponibles."""
    names = ["categorias", "categories"]
    lock = "role:ADMIN"
    description = "Muestra todas las categorías de rooms/items"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            room_cats = tag_service.get_all_categories_from_rooms()
            item_cats = tag_service.get_all_categories_from_items()

            output = "📂 <b>Categorías disponibles:</b>\n\n"

            if room_cats:
                output += "<b>Rooms:</b>\n"
                output += "\n".join(f"  • {cat}" for cat in sorted(room_cats))
            else:
                output += "<b>Rooms:</b> Ninguna categoría definida"

            output += "\n\n"

            if item_cats:
                output += "<b>Items:</b>\n"
                output += "\n".join(f"  • {cat}" for cat in sorted(item_cats))
            else:
                output += "<b>Items:</b> Ninguna categoría definida"

            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Error al mostrar categorías.")
            logging.exception(f"Error en /categorias para {character.name}")


class CmdShowTags(Command):
    """Muestra todos los tags disponibles."""
    names = ["tags", "etiquetas"]
    lock = "role:ADMIN"
    description = "Muestra todos los tags de rooms/items"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            room_tags = tag_service.get_all_tags_from_rooms()
            item_tags = tag_service.get_all_tags_from_items()

            output = "🏷️ <b>Tags disponibles:</b>\n\n"

            if room_tags:
                output += "<b>Rooms:</b>\n"
                output += ", ".join(sorted(room_tags))
            else:
                output += "<b>Rooms:</b> Ningún tag definido"

            output += "\n\n"

            if item_tags:
                output += "<b>Items:</b>\n"
                output += ", ".join(sorted(item_tags))
            else:
                output += "<b>Items:</b> Ningún tag definido"

            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Error al mostrar tags.")
            logging.exception(f"Error en /tags para {character.name}")


# Exportar todos los comandos de búsqueda
SEARCH_COMMANDS = [
    CmdListRooms(),
    CmdListItems(),
    CmdShowCategories(),
    CmdShowTags(),
]
