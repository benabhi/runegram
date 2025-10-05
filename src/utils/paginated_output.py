# src/utils/paginated_output.py
"""
Utilidades de Output Paginado.

Este módulo provee funciones helper de alto nivel para enviar listas paginadas
con navegación dual (comandos de texto + botones inline), combinando:
- Sistema de paginación (pagination.py)
- Templates (template_engine.py)
- Botones inline (inline_keyboards.py)

El objetivo es hacer trivial agregar paginación completa a cualquier comando.
"""

from typing import List, Any, Dict, Optional
from aiogram import types

from src.utils.pagination import paginate_list
from src.templates import render_template
from src.utils.inline_keyboards import create_pagination_keyboard


async def send_paginated_list(
    message: types.Message,
    items: List[Any],
    page: int,
    template_name: str,
    callback_action: str,
    per_page: int = 30,
    edit: bool = False,
    **template_context
) -> None:
    """
    Envía una lista paginada con template y botones de navegación inline.

    Esta función es un "all-in-one" que:
    1. Pagina la lista de items
    2. Renderiza el template con los items de la página actual
    3. Agrega botones inline de navegación (⬅️ Anterior | 📄 X/Y | Siguiente ➡️)
    4. Envía o edita el mensaje según el parámetro 'edit'

    Args:
        message: Mensaje de Telegram (para enviar o editar)
        items: Lista completa de items a paginar
        page: Número de página actual (1-indexed)
        template_name: Nombre del template Jinja2 (ej: "room_list.html.j2")
        callback_action: Acción base para callbacks (ej: "pg_items", "pg_rooms")
        per_page: Items por página (default: 30)
        edit: Si True, edita el mensaje existente; si False, envía nuevo mensaje
        **template_context: Contexto adicional para el template (filtros, etc.)

    Returns:
        None

    Examples:
        >>> # Uso simple sin filtros
        >>> await send_paginated_list(
        ...     message=message,
        ...     items=all_items,
        ...     page=2,
        ...     template_name="item_list.html.j2",
        ...     callback_action="pg_items"
        ... )

        >>> # Uso con filtros preservados
        >>> await send_paginated_list(
        ...     message=message,
        ...     items=filtered_rooms,
        ...     page=1,
        ...     template_name="room_list.html.j2",
        ...     callback_action="pg_rooms",
        ...     filters=True,
        ...     cat="ciudad",
        ...     tags=["seguro", "social"],
        ...     c="ciudad",  # Para callback_data (abreviado)
        ...     t="seguro,social"  # Para callback_data (abreviado)
        ... )
    """
    # 1. Paginar lista
    pagination = paginate_list(items, page=page, per_page=per_page)

    # 2. Extraer parámetros para callbacks (excluir contexto de template)
    callback_params = _extract_callback_params(template_context)

    # 3. Renderizar template con items de la página
    output = render_template(
        template_name,
        items=pagination['items'],
        page=pagination['page'],
        total_pages=pagination['total_pages'],
        total_items=pagination['total_items'],
        has_next=pagination['has_next'],
        has_prev=pagination['has_prev'],
        **template_context
    )

    # 4. Crear botones de navegación (solo si hay más de 1 página)
    keyboard = None
    if pagination['total_pages'] > 1:
        keyboard = create_pagination_keyboard(
            page=pagination['page'],
            total_pages=pagination['total_pages'],
            callback_action=callback_action,
            **callback_params
        )

    # 5. Enviar o editar mensaje
    if edit:
        await message.edit_text(output, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(output, parse_mode="HTML", reply_markup=keyboard)


async def send_paginated_simple(
    message: types.Message,
    items: List[Any],
    page: int,
    callback_action: str,
    format_func: callable,
    header: str,
    per_page: int = 30,
    edit: bool = False,
    icon: str = "📋",
    **callback_params
) -> None:
    """
    Envía una lista paginada simple sin template (formato manual).

    Útil para listados simples que no requieren un template completo.

    Args:
        message: Mensaje de Telegram
        items: Lista completa de items a paginar
        page: Número de página actual
        callback_action: Acción base para callbacks
        format_func: Función para formatear cada item (recibe item, retorna str)
        header: Encabezado del listado
        per_page: Items por página
        edit: Si True, edita mensaje; si False, envía nuevo
        icon: Ícono para el encabezado
        **callback_params: Parámetros adicionales para callbacks

    Examples:
        >>> await send_paginated_simple(
        ...     message=message,
        ...     items=characters,
        ...     page=1,
        ...     callback_action="pg_chars",
        ...     format_func=lambda c: f"{c.name} ({c.room.name})",
        ...     header="Personajes en la Sala"
        ... )
    """
    # Paginar lista
    pagination = paginate_list(items, page=page, per_page=per_page)

    # Construir output manual
    lines = [
        f"{icon} <b>{header}</b>",
        "─────────────────────────────"
    ]

    if not pagination['items']:
        lines.append("No hay elementos para mostrar.")
    else:
        for idx, item in enumerate(pagination['items'], start=pagination['start_index']):
            formatted = format_func(item)
            lines.append(f"{idx}. {formatted}")

    # Agregar info de paginación si hay múltiples páginas
    if pagination['total_pages'] > 1:
        lines.append("")
        lines.append(f"Página {pagination['page']} de {pagination['total_pages']} ({pagination['total_items']} items totales)")

    output = "<pre>" + "\n".join(lines) + "</pre>"

    # Crear botones de navegación
    keyboard = None
    if pagination['total_pages'] > 1:
        keyboard = create_pagination_keyboard(
            page=pagination['page'],
            total_pages=pagination['total_pages'],
            callback_action=callback_action,
            **callback_params
        )

    # Enviar o editar mensaje
    if edit:
        await message.edit_text(output, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(output, parse_mode="HTML", reply_markup=keyboard)


def parse_page_from_args(args: List[str], default: int = 1) -> int:
    """
    Parsea el número de página desde los argumentos del comando.

    Busca el último argumento numérico en la lista de argumentos.
    Si no encuentra ninguno, retorna el valor por defecto.

    Args:
        args: Lista de argumentos del comando
        default: Valor por defecto si no se encuentra página (default: 1)

    Returns:
        int: Número de página (mínimo 1)

    Examples:
        >>> parse_page_from_args(["cat:ciudad", "2"])
        2
        >>> parse_page_from_args(["tag:seguro,social", "5"])
        5
        >>> parse_page_from_args(["cat:ciudad"])
        1
        >>> parse_page_from_args([])
        1
    """
    if not args:
        return default

    # Buscar último argumento numérico
    for arg in reversed(args):
        try:
            page = int(arg)
            return max(1, page)  # Asegurar que sea al menos 1
        except ValueError:
            continue

    return default


def remove_page_from_args(args: List[str]) -> List[str]:
    """
    Remueve el argumento de página de la lista de argumentos.

    Útil para comandos que aceptan filtros Y página, donde necesitas
    separar la página de los filtros.

    Args:
        args: Lista de argumentos del comando

    Returns:
        list: Lista de argumentos sin el número de página

    Examples:
        >>> remove_page_from_args(["cat:ciudad", "tag:seguro", "3"])
        ["cat:ciudad", "tag:seguro"]
        >>> remove_page_from_args(["tag:exterior"])
        ["tag:exterior"]
    """
    if not args:
        return []

    # Remover último argumento si es numérico
    if args and args[-1].isdigit():
        return args[:-1]

    return args


def _extract_callback_params(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrae solo los parámetros relevantes para callback_data.

    Filtra el contexto de template para quedarse solo con parámetros
    que deben preservarse en los callbacks (filtros, etc.).

    Args:
        context: Diccionario completo de contexto de template

    Returns:
        dict: Parámetros para callback_data

    Notes:
        Los parámetros que comienzan con una letra (a-z) se consideran
        abreviaciones para callbacks (ej: "c" para category, "t" para tags).
    """
    # Parámetros válidos para callbacks (abreviaciones de 1-2 letras)
    valid_keys = ["c", "t", "cat", "tag", "type", "r_id", "char_id"]

    callback_params = {}
    for key, value in context.items():
        if key in valid_keys and value is not None:
            callback_params[key] = value

    return callback_params
