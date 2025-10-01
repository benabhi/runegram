# commands/player/channels.py
"""
Módulo de Comandos para la Gestión de Canales de Chat.
... (resto de la cabecera sin cambios) ...
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character
from src.services import channel_service
from game_data.channel_prototypes import CHANNEL_PROTOTYPES

class CmdChannels(Command):
    """
    Comando para listar todos los canales disponibles y el estado de suscripción del jugador.
    """
    names = ["canales"]
    description = "Muestra los canales disponibles y tu estado de suscripción."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            settings = await channel_service.get_or_create_settings(session, character)
            user_channels = settings.active_channels.get("active_channels", [])

            response = ["<b>Estado de tus Canales:</b>"]
            for key, proto in CHANNEL_PROTOTYPES.items():
                status = "✅ Activado" if key in user_channels else "❌ Desactivado"
                response.append(f"- <b>{proto['name']}</b> ({key}): {status}\n  <i>{proto['description']}</i>")

            await message.answer("\n".join(response), parse_mode="HTML")
        except Exception:
            await message.answer("❌ Ocurrió un error al listar los canales.")
            logging.exception(f"Fallo al ejecutar /canales para {character.name}")

class CmdEnableChannel(Command):
    """
    Comando para que un jugador se suscriba (active) un canal.
    """
    names = ["activarcanal"]
    description = "Activa un canal para recibir sus mensajes. Uso: /activarcanal [nombre]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            await message.answer("Uso: /activarcanal [nombre_del_canal]")
            return

        channel_key = args[0].lower()

        try:
            await channel_service.set_channel_status(session, character, channel_key, activate=True)
            await message.answer(f"✅ Has activado el canal '{channel_key}'.")
        except ValueError as e:
            await message.answer(f"❌ Error: {e}")
        except Exception:
            await message.answer("❌ Ocurrió un error al activar el canal.")
            logging.exception(f"Fallo al ejecutar /activarcanal para {character.name}")

class CmdDisableChannel(Command):
    """
    Comando para que un jugador cancele la suscripción (desactive) de un canal.
    """
    names = ["desactivarcanal"]
    description = "Desactiva un canal para no recibir sus mensajes. Uso: /desactivarcanal [nombre]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            await message.answer("Uso: /desactivarcanal [nombre_del_canal]")
            return

        channel_key = args[0].lower()

        try:
            await channel_service.set_channel_status(session, character, channel_key, activate=False)
            await message.answer(f"✅ Has desactivado el canal '{channel_key}'.")
        except ValueError as e:
            await message.answer(f"❌ Error: {e}")
        except Exception:
            await message.answer("❌ Ocurrió un error al desactivar el canal.")
            logging.exception(f"Fallo al ejecutar /desactivarcanal para {character.name}")

# Exportamos la lista de comandos de gestión de canales.
CHANNEL_COMMANDS = [
    CmdChannels(),
    CmdEnableChannel(),
    CmdDisableChannel(),
]