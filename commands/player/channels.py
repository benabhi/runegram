# commands/player/channels.py
"""
Módulo de Comandos para la Interacción con Canales de Chat.

Este archivo contiene los comandos que permiten a los jugadores gestionar
sus suscripciones a canales y comunicarse a través de ellos.

Incluye:
- Comandos de gestión (ej: /canales, /canal).
- Un comando específico por cada canal de tipo 'CHAT' (ej: /novato).
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character
from src.services import channel_service
from game_data.channel_prototypes import CHANNEL_PROTOTYPES

class CmdChannel(Command):
    """
    Comando para que un jugador active o desactive un canal.
    """
    names = ["canal"]
    description = "Activa o desactiva un canal. Uso: /canal [activar|desactivar] [nombre]."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        # 1. Validar la entrada del usuario (acción y nombre del canal).
        if not args or len(args) < 2 or args[0].lower() not in ["activar", "desactivar"]:
            await message.answer("Uso: /canal [activar|desactivar] [nombre_canal]")
            return

        action = args[0].lower()
        channel_key = args[1].lower()

        try:
            # 2. Llamar al servicio para persistir el cambio en la configuración del personaje.
            await channel_service.set_channel_status(session, character, channel_key, activate=(action == "activar"))
            await message.answer(f"✅ Has {action}do el canal '{channel_key}'.")
        except ValueError as e:
            # Captura el error si el `channel_key` no existe.
            await message.answer(f"❌ Error: {e}")
        except Exception:
            await message.answer("❌ Ocurrió un error al modificar el estado del canal.")
            logging.exception(f"Fallo al ejecutar /canal para {character.name}")

class CmdChannels(Command):
    """
    Comando para listar todos los canales disponibles y el estado de suscripción del jugador.
    """
    names = ["canales"]
    description = "Muestra los canales disponibles y su estado (activado/desactivado)."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            # 1. Obtener la configuración de canales del jugador.
            settings = await channel_service.get_or_create_settings(session, character)
            user_channels = settings.active_channels.get("active_channels", [])

            # 2. Construir la lista formateada para el mensaje.
            response = ["<b>Estado de tus Canales:</b>"]
            for key, proto in CHANNEL_PROTOTYPES.items():
                status = "✅ Activado" if key in user_channels else "❌ Desactivado"
                response.append(f"- <b>{proto['name']}</b> ({key}): {status}\n  <i>{proto['description']}</i>")

            await message.answer("\n".join(response), parse_mode="HTML")
        except Exception:
            await message.answer("❌ Ocurrió un error al listar los canales.")
            logging.exception(f"Fallo al ejecutar /canales para {character.name}")


class CmdNovato(Command):
    """
    Comando para enviar un mensaje al canal 'novato'.
    """
    names = ["novato"]
    lock = ""
    description = "Envía un mensaje por el canal de ayuda para novatos."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            if not args:
                await message.answer("Uso: /novato [mensaje]")
                return

            # 1. Verificar si el jugador tiene el canal activado.
            settings = await channel_service.get_or_create_settings(session, character)
            if not await channel_service.is_channel_active(settings, "novato"):
                await message.answer("Tienes el canal 'novato' desactivado. Actívalo con:\n/canal activar novato")
                return

            # 2. Formatear y transmitir el mensaje a través del servicio.
            channel_message = f"[{character.name}] {' '.join(args)}"
            await channel_service.broadcast_to_channel(session, "novato", channel_message, exclude_character_id=character.id)

            # 3. Enviar una confirmación al propio jugador para que vea su mensaje.
            await message.answer(f"📢 <b>Novato:</b> {channel_message}", parse_mode="HTML")
        except Exception:
            await message.answer("❌ Ocurrió un error al enviar tu mensaje al canal.")
            logging.exception(f"Fallo al ejecutar /novato para {character.name}")

# Exportamos la lista de comandos de este módulo.
CHANNEL_COMMANDS = [
    CmdChannel(),
    CmdChannels(),
    CmdNovato(),
]