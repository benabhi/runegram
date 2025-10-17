# commands/admin/movement.py
"""
Módulo de Comandos Administrativos para el Movimiento.

Este archivo contiene comandos que otorgan a los administradores capacidades
de movimiento especiales, que no están sujetas a las reglas normales del juego
(como las salidas definidas en una sala).

Son herramientas esenciales para la construcción, supervisión y depuración del mundo.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import player_service, command_service, narrative_service, broadcaster_service
from src.services import event_service, EventType, EventPhase, EventContext
from src.utils.presenters import show_current_room

class CmdTeleport(Command):
    """
    Comando para teletransportar al administrador a cualquier sala del juego
    especificando su ID numérico.
    """
    names = ["teleport", "tp"]
    lock = "rol(ADMIN)"  # Solo usuarios con rol ADMIN o superior pueden usarlo.
    description = "Teletranspórtate a cualquier sala usando su ID."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        # 1. Validar la entrada del usuario.
        if not args:
            await message.answer("Uso: /teleport [ID_sala]")
            return

        try:
            # Intentamos convertir el primer argumento a un número entero.
            to_room_id = int(args[0])
        except (ValueError, IndexError):
            # Falla si no hay argumentos o si el argumento no es un número.
            await message.answer("El ID de la sala debe ser un número válido.")
            return

        try:
            # 2. Guardar la sala de origen para eventos
            origin_room = character.room

            # 3. EVENTO BEFORE ON_LEAVE - Puede cancelar el teletransporte
            leave_context = EventContext(
                session=session,
                character=character,
                target=None,
                room=origin_room,
                extra={"destination_room_id": to_room_id, "teleport": True}
            )

            leave_result = await event_service.trigger_event(
                event_type=EventType.ON_LEAVE,
                phase=EventPhase.BEFORE,
                context=leave_context
            )

            # Si un script BEFORE cancela el teletransporte, detener
            if leave_result.cancel_action:
                await message.answer(leave_result.message or "No puedes salir de aquí ahora.")
                return

            # 4. Notificar a la sala de origen sobre la salida del admin
            departure_message = narrative_service.get_random_narrative(
                "teleport_departure",
                character_name=character.name
            )
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=origin_room.id,
                message_text=departure_message,
                exclude_character_id=character.id
            )

            # 5. EVENTO AFTER ON_LEAVE - Efectos al salir
            await event_service.trigger_event(
                event_type=EventType.ON_LEAVE,
                phase=EventPhase.AFTER,
                context=leave_context
            )

            # 6. Teletransportar al personaje
            await player_service.teleport_character(session, character.id, to_room_id)

            # 7. Refrescar character para obtener la nueva sala
            refreshed_character = await player_service.get_character_with_relations_by_id(session, character.id)
            destination_room = refreshed_character.room

            # 8. EVENTO BEFORE ON_ENTER - Puede cancelar la entrada
            enter_context = EventContext(
                session=session,
                character=refreshed_character,
                target=None,
                room=destination_room,
                extra={"origin_room_id": origin_room.id, "teleport": True}
            )

            enter_result = await event_service.trigger_event(
                event_type=EventType.ON_ENTER,
                phase=EventPhase.BEFORE,
                context=enter_context
            )

            # Si un script BEFORE cancela la entrada
            if enter_result.cancel_action:
                await message.answer(enter_result.message or "No puedes entrar ahí.")
                return

            # 9. Notificar a la sala de destino sobre la llegada del admin
            arrival_message = narrative_service.get_random_narrative(
                "teleport_arrival",
                character_name=character.name
            )
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=to_room_id,
                message_text=arrival_message,
                exclude_character_id=character.id
            )

            # 10. EVENTO AFTER ON_ENTER - Efectos al entrar
            await event_service.trigger_event(
                event_type=EventType.ON_ENTER,
                phase=EventPhase.AFTER,
                context=enter_context
            )

            # 11. Notificar al administrador del éxito
            await message.answer(f"🚀 Teletransportado a la sala {to_room_id}.")

            # 12. Actualizar los comandos de Telegram
            await command_service.update_telegram_commands(refreshed_character)

            # 13. Mostrar la nueva ubicación
            await show_current_room(message)

        except Exception as e:
            # Capturamos cualquier error que pueda ocurrir durante el teletransporte,
            # como un ID de sala que no existe (manejado por `player_service`).
            await message.answer(f"❌ Error al teletransportar: {e}")
            logging.warning(f"Fallo al ejecutar /teleport a la sala {args[0]}: {e}")

# Exportamos la lista de comandos de este módulo.
ADMIN_MOVEMENT_COMMANDS = [
    CmdTeleport(),
]