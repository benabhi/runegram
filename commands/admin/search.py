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
            from src.utils.paginated_output import send_paginated_list, parse_page_from_args, remove_page_from_args

            # Remover página de args para parsear solo filtros
            filter_args = remove_page_from_args(args)
            page = parse_page_from_args(args, default=1)

            items = []
            category_filter = None
            tag_filters = []

            if not filter_args:
                # Listar todos
                result = await session.execute(select(Item))
                items = result.scalars().all()
            else:
                # Parsear filtros (sintaxis cat:X tag:Y,Z)
                for arg in filter_args:
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

            # Preparar parámetros para callbacks (abreviados)
            callback_params = {}
            if category_filter:
                callback_params['c'] = category_filter
            if tag_filters:
                callback_params['t'] = ",".join(tag_filters)

            # Enviar lista paginada con template y botones
            await send_paginated_list(
                message=message,
                items=items,
                page=page,
                template_name='item_list.html.j2',
                callback_action="pg_adminitems",
                per_page=20,
                filters=bool(filter_args),
                cat=category_filter,
                tags=tag_filters,
                **callback_params  # Para preservar en botones
            )

        except Exception:
            await message.answer("❌ Error al listar items.")
            logging.exception(f"Error en /listaritems para {character.name}")


class CmdShowCategories(Command):
    """Muestra todas las categorías disponibles."""
    names = ["listarcategorias", "cats", "lcats"]
    lock = "rol(ADMIN)"
    description = "Muestra todas las categorías de salas/items. Uso: /listarcategorias [página]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            from src.utils.paginated_output import send_paginated_simple, parse_page_from_args
            from src.templates import ICONS

            page = parse_page_from_args(args, default=1)

            room_cats = sorted(tag_service.get_all_categories_from_rooms())
            item_cats = sorted(tag_service.get_all_categories_from_items())

            # Combinar en una sola lista con prefijo de tipo
            all_categories = []
            for cat in room_cats:
                all_categories.append(("🏠 Salas", cat))
            for cat in item_cats:
                all_categories.append((f"{ICONS['item']} Items", cat))

            if not all_categories:
                await message.answer(f"<pre>{ICONS['category']} No hay categorías definidas.</pre>", parse_mode="HTML")
                return

            # Función de formato
            def format_category(item):
                tipo, nombre = item
                return f"{tipo}: <i>{nombre}</i>"

            # Enviar lista paginada con botones
            await send_paginated_simple(
                message=message,
                items=all_categories,
                page=page,
                callback_action="pg_cats",
                format_func=format_category,
                header="CATEGORÍAS DISPONIBLES",
                per_page=30,
                icon=ICONS['category']
            )

        except Exception:
            await message.answer("❌ Error al mostrar categorías.")
            logging.exception(f"Error en /listarcategorias para {character.name}")


class CmdShowTags(Command):
    """Muestra todos los tags disponibles."""
    names = ["listartags", "etiquetas", "ltags"]
    lock = "rol(ADMIN)"
    description = "Muestra todos los tags de salas/items. Uso: /listartags [página]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            from src.utils.paginated_output import send_paginated_simple, parse_page_from_args
            from src.templates import ICONS

            page = parse_page_from_args(args, default=1)

            room_tags = sorted(tag_service.get_all_tags_from_rooms())
            item_tags = sorted(tag_service.get_all_tags_from_items())

            # Combinar en una sola lista con prefijo de tipo
            all_tags = []
            for tag in room_tags:
                all_tags.append(("🏠 Salas", tag))
            for tag in item_tags:
                all_tags.append((f"{ICONS['item']} Items", tag))

            if not all_tags:
                await message.answer(f"<pre>{ICONS['tag']} No hay tags definidos.</pre>", parse_mode="HTML")
                return

            # Función de formato
            def format_tag(item):
                tipo, nombre = item
                return f"{tipo}: <i>{nombre}</i>"

            # Enviar lista paginada con botones
            await send_paginated_simple(
                message=message,
                items=all_tags,
                page=page,
                callback_action="pg_tags",
                format_func=format_tag,
                header="TAGS DISPONIBLES",
                per_page=30,
                icon=ICONS['tag']
            )

        except Exception:
            await message.answer("❌ Error al mostrar tags.")
            logging.exception(f"Error en /listartags para {character.name}")


# Exportar todos los comandos de búsqueda
SEARCH_COMMANDS = [
    CmdListItems(),
    CmdShowCategories(),
    CmdShowTags(),
]
