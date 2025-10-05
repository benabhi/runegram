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
    description = "Lista items. Uso: /listaritems [cat:X] [tag:Y,Z]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            from src.templates import render_template

            items = []
            category_filter = None
            tag_filters = []

            if not args:
                # Listar todos
                result = await session.execute(select(Item))
                items = result.scalars().all()
            else:
                # Parsear filtros (nueva sintaxis)
                for arg in args:
                    if arg.startswith("cat:"):
                        category_filter = arg.split(":", 1)[1]
                    elif arg.startswith("tag:"):
                        # Soportar múltiples tags separados por coma
                        tags = arg.split(":", 1)[1].split(",")
                        tag_filters.extend([t.strip() for t in tags])

                # Ejecutar búsqueda
                if category_filter:
                    items = await tag_service.find_items_by_category(session, category_filter)
                elif tag_filters:
                    items = await tag_service.find_items_by_tags_all(session, tag_filters)
                else:
                    result = await session.execute(select(Item))
                    items = result.scalars().all()

            # Renderizar con template
            output = render_template('item_list.html.j2',
                items=items,
                max_items=20,
                filters=bool(args),
                cat=category_filter,
                tags=tag_filters
            )

            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Error al listar items.")
            logging.exception(f"Error en /listaritems para {character.name}")


class CmdShowCategories(Command):
    """Muestra todas las categorías disponibles."""
    names = ["listarcategorias", "cats", "lcats"]
    lock = "rol(ADMIN)"
    description = "Muestra todas las categorías de salas/items"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            from src.templates import render_template

            room_cats = tag_service.get_all_categories_from_rooms()
            item_cats = tag_service.get_all_categories_from_items()

            # Renderizar con template
            output = render_template('categories_list.html.j2',
                room_categories=room_cats,
                item_categories=item_cats
            )

            await message.answer(output, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Error al mostrar categorías.")
            logging.exception(f"Error en /listarcategorias para {character.name}")


class CmdShowTags(Command):
    """Muestra todos los tags disponibles."""
    names = ["listartags", "etiquetas", "ltags"]
    lock = "rol(ADMIN)"
    description = "Muestra todos los tags de salas/items"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            from src.templates import render_template

            room_tags = tag_service.get_all_tags_from_rooms()
            item_tags = tag_service.get_all_tags_from_items()

            # Renderizar con template
            output = render_template('tags_list.html.j2',
                room_tags=room_tags,
                item_tags=item_tags
            )

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
