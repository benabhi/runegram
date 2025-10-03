# src/utils/pagination.py
"""
Utilidades de Paginación.

Este módulo provee funciones helper para paginar listas largas de elementos,
permitiendo mostrar resultados en múltiples páginas para mejorar la UX en móvil.
"""

from typing import TypeVar, List, Dict, Any

T = TypeVar('T')


def paginate_list(
    items: List[T],
    page: int = 1,
    per_page: int = 30
) -> Dict[str, Any]:
    """
    Pagina una lista de items y retorna metadata útil.

    Args:
        items: Lista completa de items a paginar
        page: Número de página (1-indexed)
        per_page: Cantidad de items por página (default: 30)

    Returns:
        Dict con:
        - items: Slice de items para la página solicitada
        - page: Número de página actual
        - total_pages: Total de páginas disponibles
        - total_items: Total de items en la lista completa
        - has_next: Boolean indicando si hay página siguiente
        - has_prev: Boolean indicando si hay página anterior
        - start_index: Índice del primer item en esta página (1-indexed)
        - end_index: Índice del último item en esta página (1-indexed)

    Example:
        >>> items = list(range(1, 101))  # 100 items
        >>> result = paginate_list(items, page=2, per_page=30)
        >>> result['items']
        [31, 32, ..., 60]
        >>> result['page']
        2
        >>> result['total_pages']
        4
    """
    # Validar página
    if page < 1:
        page = 1

    total_items = len(items)

    # Calcular total de páginas
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1

    # Si la página solicitada excede el total, mostrar última página
    if page > total_pages:
        page = total_pages

    # Calcular índices de slice
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    # Obtener items de la página
    page_items = items[start_idx:end_idx]

    return {
        'items': page_items,
        'page': page,
        'total_pages': total_pages,
        'total_items': total_items,
        'has_next': page < total_pages,
        'has_prev': page > 1,
        'start_index': start_idx + 1 if page_items else 0,
        'end_index': start_idx + len(page_items) if page_items else 0,
    }


def format_pagination_footer(
    page: int,
    total_pages: int,
    command_name: str,
    total_items: int = None
) -> str:
    """
    Genera un footer informativo para outputs paginados.

    Args:
        page: Número de página actual
        total_pages: Total de páginas
        command_name: Nombre del comando para navegación
        total_items: Total de items (opcional, para mostrar conteo)

    Returns:
        String formateado con instrucciones de navegación

    Example:
        >>> format_pagination_footer(2, 5, '/items', 127)
        '\\nPágina 2 de 5 (127 items totales)\\nUsa /items 3 para siguiente página.'
    """
    lines = []

    # Línea de información de página
    if total_items:
        lines.append(f"Página {page} de {total_pages} ({total_items} items totales)")
    else:
        lines.append(f"Página {page} de {total_pages}")

    # Instrucciones de navegación
    nav_instructions = []
    if page < total_pages:
        nav_instructions.append(f"{command_name} {page + 1} para siguiente")
    if page > 1:
        nav_instructions.append(f"{command_name} {page - 1} para anterior")

    if nav_instructions:
        lines.append(f"Usa {' | '.join(nav_instructions)}.")

    return "\n" + "\n".join(lines)
