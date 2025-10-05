# src/utils/inline_keyboards.py
"""
Módulo de Utilidades para Botones Inline de Telegram.

Este módulo centraliza la creación de teclados inline (InlineKeyboardMarkup) para
mejorar la experiencia de usuario en Telegram, permitiendo interacción mediante
botones en lugar de comandos de texto.

El sistema está diseñado para ser:
- Escalable: Fácil agregar nuevos tipos de botones
- Mantenible: Funciones reutilizables y bien documentadas
- Robusto: Formato estructurado de callback_data
- Preparado para futuro teclado dinámico completo

Responsabilidades:
1. Crear teclados inline para diferentes contextos del juego
2. Generar callback_data estructurado y parseable
3. Proveer helpers para botones comunes
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any, Optional
from src.models import Room
from src.templates import get_direction_icon


# ===========================
# Sistema de Callback Data
# ===========================

def create_callback_data(action: str, **params) -> str:
    """
    Crea una cadena de callback_data estructurada y parseable.

    Formato: "action:param1=value1:param2=value2"
    Máximo: 64 bytes (limitación de Telegram)

    Args:
        action: La acción a realizar (ej: "move", "create_char", "use_item")
        **params: Parámetros adicionales como pares clave-valor

    Returns:
        str: Callback_data formateado

    Examples:
        >>> create_callback_data("move", direction="norte")
        "move:direction=norte"
        >>> create_callback_data("use_item", item_id=5)
        "use_item:item_id=5"
    """
    parts = [action]
    for key, value in params.items():
        parts.append(f"{key}={value}")
    return ":".join(parts)


def parse_callback_data(callback_data: str) -> Dict[str, Any]:
    """
    Parsea una cadena de callback_data en un diccionario.

    Args:
        callback_data: Cadena en formato "action:param1=value1:param2=value2"

    Returns:
        dict: {'action': str, 'params': dict} con la acción y parámetros

    Examples:
        >>> parse_callback_data("move:direction=norte")
        {'action': 'move', 'params': {'direction': 'norte'}}
    """
    parts = callback_data.split(":")
    action = parts[0]
    params = {}

    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            # Intentar convertir a int si es posible
            try:
                value = int(value)
            except ValueError:
                pass
            params[key] = value

    return {"action": action, "params": params}


# ===========================
# Botones de Creación de Personaje
# ===========================

def create_character_creation_keyboard() -> InlineKeyboardMarkup:
    """
    Crea un teclado inline con botón para iniciar la creación de personaje.

    Este botón inicia un flujo FSM (Finite State Machine) que solicita
    el nombre del personaje de forma interactiva y robusta.

    Returns:
        InlineKeyboardMarkup: Teclado con botón "Crear personaje"
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    button = InlineKeyboardButton(
        text="✨ Crear personaje",
        callback_data=create_callback_data("create_char", step="start")
    )
    keyboard.add(button)
    return keyboard


# ===========================
# Botones de Navegación de Salas
# ===========================

def create_room_navigation_keyboard(room: Room) -> Optional[InlineKeyboardMarkup]:
    """
    Crea un teclado inline con botones para las salidas disponibles en una sala.

    Cada botón ejecuta el comando de movimiento correspondiente cuando se presiona.
    Los botones incluyen el ícono de dirección para mejor UX.

    Args:
        room: Objeto Room con las salidas cargadas (room.exits_from)

    Returns:
        InlineKeyboardMarkup o None: Teclado con botones de salidas, o None si no hay salidas

    Examples:
        Si la sala tiene salidas "norte" y "sur":
        [ ⬆️ Norte ] [ ⬇️ Sur ]
    """
    if not room.exits_from:
        return None

    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = []

    # Ordenar salidas alfabéticamente para consistencia
    sorted_exits = sorted(room.exits_from, key=lambda e: e.name)

    for exit in sorted_exits:
        # Obtener ícono de dirección
        icon = get_direction_icon(exit.name)
        direction_name = exit.name.capitalize()

        # Crear botón
        button = InlineKeyboardButton(
            text=f"{icon} {direction_name}",
            callback_data=create_callback_data("move", direction=exit.name)
        )
        buttons.append(button)

    # Agregar botones de 2 en 2 para mejor disposición
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.row(buttons[i], buttons[i + 1])
        else:
            keyboard.row(buttons[i])

    return keyboard


# ===========================
# Botones de Inventario (Futuro)
# ===========================

def create_inventory_keyboard(items: List, page: int = 1, per_page: int = 5) -> InlineKeyboardMarkup:
    """
    Crea un teclado inline para interactuar con items del inventario.

    FUTURO: Este es un placeholder para el teclado dinámico completo.
    Permitirá usar, examinar, dejar, etc. items directamente con botones.

    Args:
        items: Lista de items
        page: Página actual
        per_page: Items por página

    Returns:
        InlineKeyboardMarkup: Teclado con botones de items (futuro)
    """
    # TODO: Implementar cuando se desarrolle el teclado dinámico completo
    keyboard = InlineKeyboardMarkup()
    return keyboard


# ===========================
# Botones de Confirmación
# ===========================

def create_confirmation_keyboard(action: str, **params) -> InlineKeyboardMarkup:
    """
    Crea un teclado inline de confirmación Sí/No.

    Útil para acciones destructivas o importantes que requieren confirmación.

    Args:
        action: La acción a confirmar (ej: "delete_char", "drop_item")
        **params: Parámetros adicionales para la acción

    Returns:
        InlineKeyboardMarkup: Teclado con botones ✅ Sí / ❌ No

    Examples:
        >>> create_confirmation_keyboard("delete_char", char_id=5)
        [ ✅ Sí ] [ ❌ No ]
    """
    keyboard = InlineKeyboardMarkup(row_width=2)

    yes_button = InlineKeyboardButton(
        text="✅ Sí",
        callback_data=create_callback_data(f"confirm_{action}", confirm="yes", **params)
    )
    no_button = InlineKeyboardButton(
        text="❌ No",
        callback_data=create_callback_data(f"confirm_{action}", confirm="no", **params)
    )

    keyboard.row(yes_button, no_button)
    return keyboard


# ===========================
# Helper: Botón de Actualizar
# ===========================

def create_refresh_button(context: str) -> InlineKeyboardButton:
    """
    Crea un botón individual de "Actualizar" para refrescar información.

    Args:
        context: El contexto a refrescar (ej: "room", "inventory", "who")

    Returns:
        InlineKeyboardButton: Botón "🔄 Actualizar"
    """
    return InlineKeyboardButton(
        text="🔄 Actualizar",
        callback_data=create_callback_data("refresh", context=context)
    )


# ===========================
# Botones de Paginación
# ===========================

def create_pagination_keyboard(
    page: int,
    total_pages: int,
    callback_action: str,
    **params
) -> InlineKeyboardMarkup:
    """
    Crea un teclado inline con botones de navegación de páginas.

    Genera botones [ ⬅️ Anterior ] [ 📄 X/Y ] [ Siguiente ➡️ ] que permiten
    navegar entre páginas sin necesidad de escribir comandos.

    Args:
        page: Número de página actual (1-indexed)
        total_pages: Total de páginas disponibles
        callback_action: Acción base para el callback (ej: "pg_items", "pg_rooms")
        **params: Parámetros adicionales a preservar (filtros, etc.)

    Returns:
        InlineKeyboardMarkup: Teclado con botones de navegación

    Examples:
        >>> # Paginación simple sin filtros
        >>> keyboard = create_pagination_keyboard(2, 5, "pg_items")

        >>> # Paginación con filtros preservados
        >>> keyboard = create_pagination_keyboard(
        ...     page=3,
        ...     total_pages=10,
        ...     callback_action="pg_rooms",
        ...     c="ciudad",  # c = category (abreviado)
        ...     t="seguro,social"  # t = tags (abreviado)
        ... )
    """
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = []

    # Botón "Anterior" (solo si no es la primera página)
    if page > 1:
        prev_button = InlineKeyboardButton(
            text="⬅️ Anterior",
            callback_data=create_callback_data(callback_action, p=page - 1, **params)
        )
        buttons.append(prev_button)
    else:
        # Botón deshabilitado (espacio en blanco)
        buttons.append(InlineKeyboardButton(text=" ", callback_data="noop"))

    # Botón de información de página (no hace nada, solo muestra info)
    page_info_button = InlineKeyboardButton(
        text=f"📄 {page}/{total_pages}",
        callback_data="noop"  # No hace nada
    )
    buttons.append(page_info_button)

    # Botón "Siguiente" (solo si no es la última página)
    if page < total_pages:
        next_button = InlineKeyboardButton(
            text="Siguiente ➡️",
            callback_data=create_callback_data(callback_action, p=page + 1, **params)
        )
        buttons.append(next_button)
    else:
        # Botón deshabilitado (espacio en blanco)
        buttons.append(InlineKeyboardButton(text=" ", callback_data="noop"))

    keyboard.row(*buttons)
    return keyboard
