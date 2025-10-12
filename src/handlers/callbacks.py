# src/handlers/callbacks.py
"""
Módulo de Manejo de Callbacks de Botones Inline.

Este handler centraliza el procesamiento de todos los clics en botones inline
de Telegram. Actúa como router que distribuye las acciones a las funciones
correspondientes según el callback_data recibido.

El sistema está diseñado para:
- Escalabilidad: Fácil agregar nuevas acciones
- Mantenibilidad: Router centralizado y bien estructurado
- Robustez: Manejo de errores y validaciones
- Preparado para teclado dinámico completo en el futuro

Responsabilidades:
1. Recibir y parsear callbacks de botones inline
2. Validar permisos y estado del jugador
3. Rutear a la función handler correspondiente
4. Proporcionar feedback visual (answer/alert)
"""

import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.dispatcher import dp
from src.db import async_session_factory
from src.services import player_service, online_service
from src.utils.inline_keyboards import parse_callback_data
from src.utils.presenters import show_current_room


# ===========================
# Estados FSM para Creación de Personaje
# ===========================

class CharacterCreationStates(StatesGroup):
    """Estados del flujo de creación de personaje con FSM."""
    waiting_for_name = State()


# ===========================
# Handlers de Acciones Específicas
# ===========================

async def handle_character_creation(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """
    Inicia el flujo de creación de personaje usando FSM.

    Este handler se invoca cuando el jugador presiona el botón "Crear personaje".
    Inicia un estado FSM que espera el nombre del personaje.

    Args:
        callback: Callback query de Telegram
        params: Parámetros del callback_data
        session: Sesión de base de datos
    """
    # Verificar que el jugador no tenga ya un personaje
    account = await player_service.get_or_create_account(session, callback.from_user.id)

    if account.character:
        await callback.answer("Ya tienes un personaje creado.", show_alert=True)
        return

    # Iniciar FSM
    state = dp.current_state(user=callback.from_user.id)
    await state.set_state(CharacterCreationStates.waiting_for_name)

    from src.config import settings

    await callback.message.edit_text(
        "✨ <b>Creación de Personaje</b>\n\n"
        "Por favor, escribe el nombre que deseas para tu personaje.\n\n"
        "<i>Ejemplo: Aragorn</i>\n\n"
        f"El nombre debe tener entre {settings.characters_name_min_length} y {settings.characters_name_max_length} "
        "caracteres y solo puede contener letras (sin espacios).",
        parse_mode="HTML"
    )
    await callback.answer()


async def handle_movement(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """
    Maneja el movimiento del personaje a través de botones inline.

    Args:
        callback: Callback query de Telegram
        params: Parámetros del callback_data (debe incluir 'direction')
        session: Sesión de base de datos
    """
    direction = params.get("direction")
    if not direction:
        await callback.answer("Error: Dirección no especificada.", show_alert=True)
        return

    # Obtener personaje
    account = await player_service.get_or_create_account(session, callback.from_user.id)
    if not account.character:
        await callback.answer("Primero debes crear un personaje.", show_alert=True)
        return

    character = account.character

    # Actualizar actividad
    await online_service.update_last_seen(session, character)

    # Buscar la salida en la sala actual
    exit_found = None
    for exit in character.room.exits_from:
        if exit.name.lower() == direction.lower():
            exit_found = exit
            break

    if not exit_found:
        await callback.answer(f"No hay salida hacia {direction}.", show_alert=True)
        return

    # Verificar permisos de la salida (si tiene lock)
    if exit_found.locks:
        from src.services import permission_service
        can_use, error_msg = await permission_service.can_execute(character, exit_found.locks)
        if not can_use:
            await callback.answer(error_msg or "No puedes usar esa salida.", show_alert=True)
            return

    # Obtener sala de destino
    if not exit_found.to_room:
        await callback.answer("Error: Salida sin destino.", show_alert=True)
        return

    # Notificaciones sociales
    from src.services import broadcaster_service, command_service

    old_room_id = character.room_id
    new_room_id = exit_found.to_room_id

    # Notificar a la sala de origen
    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=old_room_id,
        message_text=f"<i>{character.name} se ha ido hacia {direction}.</i>",
        exclude_character_id=character.id
    )

    # Mover al personaje usando el servicio
    await player_service.teleport_character(session, character.id, new_room_id)

    # Notificar a la sala de destino
    opposite_direction = {
        "norte": "sur", "sur": "norte",
        "este": "oeste", "oeste": "este",
        "noreste": "suroeste", "suroeste": "noreste",
        "noroeste": "sureste", "sureste": "noroeste",
        "arriba": "abajo", "abajo": "arriba"
    }.get(direction.lower(), "otra dirección")

    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=new_room_id,
        message_text=f"<i>{character.name} ha llegado desde {opposite_direction}.</i>",
        exclude_character_id=character.id
    )

    # Actualizar comandos de Telegram (por si la sala otorga nuevos command sets)
    refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
    if refreshed_character:
        await command_service.update_telegram_commands(refreshed_character)

    # Mostrar nueva sala al jugador (con botones)
    # IMPORTANTE: Pasamos session Y character para evitar usar telegram_id incorrecto del mensaje
    # edit=False para enviar mensaje nuevo y mantener historial de movimientos
    await show_current_room(callback.message, edit=False, session=session, character=refreshed_character)
    await callback.answer()


async def handle_refresh(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """
    Maneja la acción de refrescar/actualizar información.

    Args:
        callback: Callback query de Telegram
        params: Parámetros del callback_data (debe incluir 'context')
        session: Sesión de base de datos
    """
    context = params.get("context")

    if context == "room":
        # Obtener el character correcto usando callback.from_user.id (no message.from_user.id)
        account = await player_service.get_or_create_account(session, callback.from_user.id)
        if not account or not account.character:
            await callback.answer("Primero debes crear un personaje.", show_alert=True)
            return

        # Refrescar vista de sala pasando session y character
        await show_current_room(callback.message, edit=True, session=session, character=account.character)
        await callback.answer("Sala actualizada.")
    else:
        await callback.answer("Contexto de actualización desconocido.", show_alert=True)


# ===========================
# Handlers de Paginación
# ===========================

async def handle_paginate_items(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """
    Maneja la paginación del comando /items (items en sala).

    Args:
        callback: Callback query de Telegram
        params: Parámetros del callback_data (debe incluir 'p' para página)
        session: Sesión de base de datos
    """
    page = params.get("p", 1)

    # Obtener personaje
    account = await player_service.get_or_create_account(session, callback.from_user.id)
    if not account.character:
        await callback.answer("Primero debes crear un personaje.", show_alert=True)
        return

    character = account.character
    room = character.room
    items = room.items

    if not items:
        await callback.answer("No hay items en esta sala.", show_alert=True)
        return

    # Importar helper y re-enviar lista paginada (editando mensaje)
    from src.utils.paginated_output import send_paginated_simple
    from src.templates import ICONS
    from src.config import settings

    def format_item(item):
        item_icon = item.prototype.get('display', {}).get('icon', ICONS['item'])
        return f"{item_icon} {item.get_name()}"

    await send_paginated_simple(
        message=callback.message,
        items=items,
        page=page,
        callback_action="pg_items",
        format_func=format_item,
        header=f"Todos los items en {room.name}",
        per_page=settings.pagination_items_per_page,
        icon=ICONS['look'],
        edit=True  # Editar mensaje existente
    )
    await callback.answer()


async def handle_paginate_characters(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """Maneja la paginación del comando /personajes."""
    page = params.get("p", 1)

    account = await player_service.get_or_create_account(session, callback.from_user.id)
    if not account.character:
        await callback.answer("Primero debes crear un personaje.", show_alert=True)
        return

    character = account.character
    room = character.room

    # Filtrar personajes activos (excluir viewer y desconectados)
    active_characters = []
    for char in room.characters:
        if char.id != character.id and await online_service.is_character_online(char.id):
            active_characters.append(char)

    if not active_characters:
        await callback.answer("Estás solo aquí.", show_alert=True)
        return

    active_characters.sort(key=lambda c: c.name)

    from src.utils.paginated_output import send_paginated_simple
    from src.templates import ICONS
    from src.config import settings

    await send_paginated_simple(
        message=callback.message,
        items=active_characters,
        page=page,
        callback_action="pg_chars",
        format_func=lambda c: c.name,
        header=f"Personajes en {room.name}",
        per_page=settings.pagination_items_per_page,
        icon=ICONS['character'],
        edit=True
    )
    await callback.answer()


async def handle_paginate_who(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """Maneja la paginación del comando /quien todo."""
    page = params.get("p", 1)

    account = await player_service.get_or_create_account(session, callback.from_user.id)
    if not account.character:
        await callback.answer("Primero debes crear un personaje.", show_alert=True)
        return

    character = account.character

    # Obtener todos los jugadores online
    online_characters = await online_service.get_online_characters(session)
    filtered_chars = [char for char in online_characters if char.id != character.id]

    if not filtered_chars:
        await callback.answer("No hay otros jugadores online.", show_alert=True)
        return

    filtered_chars.sort(key=lambda c: c.name)

    from src.utils.paginated_output import send_paginated_simple
    from src.templates import ICONS
    from src.config import settings

    def format_who_char(char):
        location = f" ({ICONS['room']} {char.room.name})" if char.room else ""
        return f"{char.name}{location}"

    await send_paginated_simple(
        message=callback.message,
        items=filtered_chars,
        page=page,
        callback_action="pg_who",
        format_func=format_who_char,
        header=f"Jugadores en Runegram ({len(online_characters)} conectados)",
        per_page=settings.pagination_items_per_page,
        icon=ICONS['player'],
        edit=True
    )
    await callback.answer()


async def handle_paginate_inventory(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """Maneja la paginación del comando /inventario todo."""
    page = params.get("p", 1)

    account = await player_service.get_or_create_account(session, callback.from_user.id)
    if not account.character:
        await callback.answer("Primero debes crear un personaje.", show_alert=True)
        return

    character = account.character
    items = character.items

    if not items:
        await callback.answer("No tienes items en tu inventario.", show_alert=True)
        return

    from src.utils.paginated_output import send_paginated_simple
    from src.templates import ICONS
    from src.config import settings

    def format_inv_item(item):
        item_icon = item.prototype.get('display', {}).get('icon', ICONS['item'])
        return f"{item_icon} {item.get_name()}"

    await send_paginated_simple(
        message=callback.message,
        items=items,
        page=page,
        callback_action="pg_inv",
        format_func=format_inv_item,
        header="Tu Inventario Completo",
        per_page=settings.pagination_items_per_page,
        icon=ICONS['inventory'],
        edit=True
    )
    await callback.answer()


async def handle_paginate_rooms(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """Maneja la paginación del comando /listarsalas (admin)."""
    page = params.get("p", 1)
    category_filter = params.get("c")  # c = category (abreviado)
    tag_filters_str = params.get("t")  # t = tags (abreviado)

    # Parsear tags si existen
    tag_filters = []
    if tag_filters_str:
        tag_filters = [t.strip() for t in tag_filters_str.split(",")]

    # Ejecutar misma lógica que el comando
    from src.services import tag_service
    from sqlalchemy import select
    from src.models import Room

    all_rooms = []
    if not category_filter and not tag_filters:
        result = await session.execute(select(Room).order_by(Room.id))
        all_rooms = result.scalars().all()
    elif category_filter:
        all_rooms = await tag_service.find_rooms_by_category(session, category_filter)
    elif tag_filters:
        all_rooms = await tag_service.find_rooms_by_tags_all(session, tag_filters)

    # Preparar parámetros para botones
    callback_params = {}
    if category_filter:
        callback_params['c'] = category_filter
    if tag_filters:
        callback_params['t'] = ",".join(tag_filters)

    from src.utils.paginated_output import send_paginated_list

    await send_paginated_list(
        message=callback.message,
        items=all_rooms,
        page=page,
        template_name='room_list.html.j2',
        callback_action="pg_rooms",
        per_page=30,
        edit=True,
        filters=bool(category_filter or tag_filters),
        cat=category_filter,
        tags=tag_filters,
        **callback_params
    )
    await callback.answer()


async def handle_paginate_admin_items(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """Maneja la paginación del comando /listaritems (admin)."""
    page = params.get("p", 1)
    category_filter = params.get("c")
    tag_filters_str = params.get("t")

    tag_filters = []
    if tag_filters_str:
        tag_filters = [t.strip() for t in tag_filters_str.split(",")]

    from src.services import tag_service
    from sqlalchemy import select
    from src.models import Item

    items = []
    if not category_filter and not tag_filters:
        result = await session.execute(select(Item))
        items = result.scalars().all()
    elif category_filter:
        items = await tag_service.find_items_by_category(session, category_filter)
    elif tag_filters:
        items = await tag_service.find_items_by_tags_all(session, tag_filters)

    callback_params = {}
    if category_filter:
        callback_params['c'] = category_filter
    if tag_filters:
        callback_params['t'] = ",".join(tag_filters)

    from src.utils.paginated_output import send_paginated_list
    from src.config import settings

    await send_paginated_list(
        message=callback.message,
        items=items,
        page=page,
        template_name='item_list.html.j2',
        callback_action="pg_adminitems",
        per_page=settings.pagination_items_per_page,
        edit=True,
        filters=bool(category_filter or tag_filters),
        cat=category_filter,
        tags=tag_filters,
        **callback_params
    )
    await callback.answer()


async def handle_paginate_categories(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """Maneja la paginación del comando /listarcategorias (admin)."""
    page = params.get("p", 1)

    from src.services import tag_service
    from src.utils.paginated_output import send_paginated_simple
    from src.templates import ICONS

    room_cats = sorted(tag_service.get_all_categories_from_rooms())
    item_cats = sorted(tag_service.get_all_categories_from_items())

    all_categories = []
    for cat in room_cats:
        all_categories.append(("🏠 Salas", cat))
    for cat in item_cats:
        all_categories.append((f"{ICONS['item']} Items", cat))

    if not all_categories:
        await callback.answer("No hay categorías definidas.", show_alert=True)
        return

    def format_category(item):
        tipo, nombre = item
        return f"{tipo}: <i>{nombre}</i>"

    await send_paginated_simple(
        message=callback.message,
        items=all_categories,
        page=page,
        callback_action="pg_cats",
        format_func=format_category,
        header="CATEGORÍAS DISPONIBLES",
        per_page=30,
        icon=ICONS['category'],
        edit=True
    )
    await callback.answer()


async def handle_paginate_tags(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """Maneja la paginación del comando /listartags (admin)."""
    page = params.get("p", 1)

    from src.services import tag_service
    from src.utils.paginated_output import send_paginated_simple
    from src.templates import ICONS

    room_tags = sorted(tag_service.get_all_tags_from_rooms())
    item_tags = sorted(tag_service.get_all_tags_from_items())

    all_tags = []
    for tag in room_tags:
        all_tags.append(("🏠 Salas", tag))
    for tag in item_tags:
        all_tags.append((f"{ICONS['item']} Items", tag))

    if not all_tags:
        await callback.answer("No hay tags definidos.", show_alert=True)
        return

    def format_tag(item):
        tipo, nombre = item
        return f"{tipo}: <i>{nombre}</i>"

    await send_paginated_simple(
        message=callback.message,
        items=all_tags,
        page=page,
        callback_action="pg_tags",
        format_func=format_tag,
        header="TAGS DISPONIBLES",
        per_page=30,
        icon=ICONS['tag'],
        edit=True
    )
    await callback.answer()


# ===========================
# Router Principal de Callbacks
# ===========================

async def handle_noop(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """
    Handler para botones que no hacen nada (deshabilitados).

    Usado para botones informativos o deshabilitados en teclados inline.
    Simplemente responde sin acción para evitar el indicador de "loading".
    """
    await callback.answer()


# Diccionario que mapea acciones a funciones handler
CALLBACK_HANDLERS = {
    "create_char": handle_character_creation,
    "move": handle_movement,
    "refresh": handle_refresh,
    "noop": handle_noop,  # Botones deshabilitados

    # Handlers de paginación
    "pg_items": handle_paginate_items,
    "pg_chars": handle_paginate_characters,
    "pg_who": handle_paginate_who,
    "pg_inv": handle_paginate_inventory,
    "pg_rooms": handle_paginate_rooms,
    "pg_adminitems": handle_paginate_admin_items,
    "pg_cats": handle_paginate_categories,
    "pg_tags": handle_paginate_tags,

    # Futuras acciones se agregan aquí:
    # "use_item": handle_use_item,
    # "drop_item": handle_drop_item,
    # "confirm_delete_char": handle_confirm_delete_char,
}


@dp.callback_query_handler(lambda c: True)
async def callback_query_router(callback: types.CallbackQuery):
    """
    Router principal que recibe todos los callback queries y los distribuye.

    Este handler intercepta TODOS los clics en botones inline y decide
    qué función específica debe manejar cada acción.
    """
    async with async_session_factory() as session:
        try:
            # Parsear callback_data
            callback_info = parse_callback_data(callback.data)
            action = callback_info["action"]
            params = callback_info["params"]

            logging.info(f"Callback recibido - Action: {action}, Params: {params}, User: {callback.from_user.id}")

            # Buscar handler correspondiente
            handler_func = CALLBACK_HANDLERS.get(action)

            if handler_func:
                await handler_func(callback, params, session)
            else:
                logging.warning(f"Acción de callback desconocida: {action}")
                await callback.answer("Acción no reconocida.", show_alert=True)

        except Exception:
            # Log completo del error
            logging.exception(f"Error manejando callback para usuario {callback.from_user.id}")
            await callback.answer("❌ Ocurrió un error al procesar la acción.", show_alert=True)


# ===========================
# Handler para Respuestas FSM
# ===========================

@dp.message_handler(state=CharacterCreationStates.waiting_for_name)
async def process_character_name(message: types.Message, state: FSMContext):
    """
    Procesa el nombre del personaje cuando el usuario responde en el flujo FSM.

    Este handler se activa cuando el FSM está en estado 'waiting_for_name'
    y el usuario envía un mensaje de texto.
    """
    async with async_session_factory() as session:
        try:
            from src.config import settings

            name = message.text.strip()

            # Validar nombre
            if len(name) < settings.characters_name_min_length:
                await message.answer(
                    f"❌ El nombre debe tener al menos {settings.characters_name_min_length} caracteres.\n"
                    "Por favor, intenta con otro nombre:"
                )
                return

            if len(name) > settings.characters_name_max_length:
                await message.answer(
                    f"❌ El nombre es demasiado largo (máximo {settings.characters_name_max_length} caracteres).\n"
                    "Por favor, intenta con otro nombre:"
                )
                return

            if not name.isalpha():
                await message.answer(
                    "❌ El nombre solo puede contener letras (sin espacios ni caracteres especiales).\n"
                    "Por favor, intenta con otro nombre:"
                )
                return

            # Verificar que el nombre no esté en uso
            from sqlalchemy import select
            from src.models import Character

            existing = await session.execute(
                select(Character).where(Character.name.ilike(name))
            )
            if existing.scalar_one_or_none():
                await message.answer(
                    f"❌ El nombre '{name}' ya está en uso.\n"
                    "Por favor, elige otro nombre:"
                )
                return

            # Crear personaje
            character = await player_service.create_character(session, message.from_user.id, name)

            # IMPORTANTE: Marcar el personaje como online inmediatamente
            await online_service.update_last_seen(session, character)

            # Finalizar FSM
            await state.finish()

            # Mostrar mensaje de bienvenida y sala inicial
            await message.answer(
                f"✨ <b>¡Bienvenido, {character.name}!</b>\n\n"
                "Tu personaje ha sido creado exitosamente.\n"
                "Tu aventura comienza ahora...",
                parse_mode="HTML"
            )

            # Actualizar comandos de Telegram y mostrar sala
            from src.services import command_service
            await command_service.update_telegram_commands(character)
            await show_current_room(message)

        except Exception:
            logging.exception(f"Error en creación de personaje para usuario {message.from_user.id}")
            await message.answer("❌ Ocurrió un error al crear tu personaje. Por favor, intenta nuevamente.")
            await state.finish()
