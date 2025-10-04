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

    await callback.message.edit_text(
        "✨ <b>Creación de Personaje</b>\n\n"
        "Por favor, escribe el nombre que deseas para tu personaje.\n\n"
        "<i>Ejemplo: Aragorn</i>\n\n"
        "El nombre debe tener entre 3 y 15 caracteres y solo puede contener letras (sin espacios).",
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
    await show_current_room(callback.message, edit=True)
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
        # Refrescar vista de sala
        await show_current_room(callback.message, edit=True)
        await callback.answer("Sala actualizada.")
    else:
        await callback.answer("Contexto de actualización desconocido.", show_alert=True)


# ===========================
# Router Principal de Callbacks
# ===========================

# Diccionario que mapea acciones a funciones handler
CALLBACK_HANDLERS = {
    "create_char": handle_character_creation,
    "move": handle_movement,
    "refresh": handle_refresh,
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
            name = message.text.strip()

            # Validar nombre
            if len(name) < 3:
                await message.answer(
                    "❌ El nombre debe tener al menos 3 caracteres.\n"
                    "Por favor, intenta con otro nombre:"
                )
                return

            if len(name) > 15:
                await message.answer(
                    "❌ El nombre es demasiado largo (máximo 15 caracteres).\n"
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
