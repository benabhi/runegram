# commands/admin/search.py
"""
Comandos de Administración para Búsqueda por Categories y Tags.

Estos comandos permiten a los administradores buscar y filtrar
Items usando el sistema de categories y tags.
"""

import logging
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character, Item
from src.services import tag_service


class CmdListItems(Command):
    """Lista items filtrados por category o tags."""
    names = ["listaritems", "litems"]
    lock = "rol(ADMIN)"
    description = "Lista items. Uso: /listaritems [category:X] [tag:Y]"

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
            logging.exception(f"Error en /listaritems para {character.name}")


class CmdShowCategories(Command):
    """Muestra todas las categorías disponibles."""
    names = ["listarcategorias", "cats"]
    lock = "rol(ADMIN)"
    description = "Muestra todas las categorías de salas/items"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            room_cats = tag_service.get_all_categories_from_rooms()
            item_cats = tag_service.get_all_categories_from_items()

            output = "📂 <b>Categorías disponibles:</b>\n\n"

            if room_cats:
                output += "<b>Salas:</b>\n"
                output += "\n".join(f"  • {cat}" for cat in sorted(room_cats))
            else:
                output += "<b>Salas:</b> Ninguna categoría definida"

            output += "\n\n"

            if item_cats:
                output += "<b>Items:</b>\n"
                output += "\n".join(f"  • {cat}" for cat in sorted(item_cats))
            else:
                output += "<b>Items:</b> Ninguna categoría definida"

            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Error al mostrar categorías.")
            logging.exception(f"Error en /listarcategorias para {character.name}")


class CmdShowTags(Command):
    """Muestra todos los tags disponibles."""
    names = ["listartags", "etiquetas"]
    lock = "rol(ADMIN)"
    description = "Muestra todos los tags de salas/items"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            room_tags = tag_service.get_all_tags_from_rooms()
            item_tags = tag_service.get_all_tags_from_items()

            output = "🏷️ <b>Tags disponibles:</b>\n\n"

            if room_tags:
                output += "<b>Salas:</b>\n"
                output += ", ".join(sorted(room_tags))
            else:
                output += "<b>Salas:</b> Ningún tag definido"

            output += "\n\n"

            if item_tags:
                output += "<b>Items:</b>\n"
                output += ", ".join(sorted(item_tags))
            else:
                output += "<b>Items:</b> Ningún tag definido"

            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Error al mostrar tags.")
            logging.exception(f"Error en /listartags para {character.name}")


# Exportar todos los comandos de búsqueda
SEARCH_COMMANDS = [
    CmdListItems(),
    CmdShowCategories(),
    CmdShowTags(),
]
