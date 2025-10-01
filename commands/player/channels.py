# commands/player/channels.py
"""
Módulo de Comandos para la Interacción con Canales de Chat.

Este archivo centraliza toda la interacción del jugador con el sistema de canales
a través de un único comando principal: `/canal`.

El comando `/canal` actúa como un router con subcomandos:
- `/canal listar`: Muestra el estado de las suscripciones.
- `/canal activar <nombre>`: Se suscribe a un canal.
- `/canal desactivar <nombre>`: Cancela la suscripción a un canal.
- `/canal <nombre> [mensaje]`: Envía un mensaje a un canal de tipo CHAT.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character
from src.services import channel_service
from game_data.channel_prototypes import CHANNEL_PROTOTYPES

class CmdCanal(Command):
    """
    Comando unificado para gestionar y hablar por los canales.
    """
    names = ["canal"]
    description = "Gestiona o habla por los canales. Uso: /canal <subcomando|nombre> [args]"

    async def _list_channels(self, character: Character, session: AsyncSession, message: types.Message):
        """Muestra al jugador el estado de sus suscripciones a canales."""
        settings = await channel_service.get_or_create_settings(session, character)
        user_channels = settings.active_channels.get("active_channels", [])

        response = ["<b>Estado de tus Canales:</b>"]
        for key, proto in CHANNEL_PROTOTYPES.items():
            status = "✅ Activado" if key in user_channels else "❌ Desactivado"
            response.append(f"- <b>{proto['name']}</b> ({key}): {status}\n  <i>{proto['description']}</i>")

        await message.answer("\n".join(response), parse_mode="HTML")

    async def _toggle_channel(self, character: Character, session: AsyncSession, message: types.Message, action: str, channel_key: str):
        """Activa o desactiva la suscripción a un canal."""
        try:
            await channel_service.set_channel_status(session, character, channel_key, activate=(action == "activar"))
            await message.answer(f"✅ Has {action}do el canal '{channel_key}'.")
        except ValueError as e:
            await message.answer(f"❌ Error: {e}")

    async def _speak_on_channel(self, character: Character, session: AsyncSession, message: types.Message, channel_key: str, text: str):
        """Envía un mensaje a un canal."""
        if channel_key not in CHANNEL_PROTOTYPES:
            await message.answer(f"El canal '{channel_key}' no existe. Usa /canal listar para ver los disponibles.")
            return

        proto = CHANNEL_PROTOTYPES[channel_key]
        if proto.get("type") != "CHAT":
            await message.answer(f"No puedes hablar en el canal '{channel_key}', es solo para anuncios.")
            return

        settings = await channel_service.get_or_create_settings(session, character)
        if not await channel_service.is_channel_active(settings, channel_key):
            await message.answer(f"Tienes el canal '{channel_key}' desactivado. Actívalo con:\n/canal activar {channel_key}")
            return

        channel_message = f"[{character.name}] {text}"
        await channel_service.broadcast_to_channel(session, channel_key, channel_message, exclude_character_id=character.id)

        # Confirmación para el que envía el mensaje.
        await message.answer(f"{proto['icon']} <b>{proto['name']}:</b> {channel_message}", parse_mode="HTML")


    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            if not args:
                await message.answer(
                    "<b>Uso del comando /canal:</b>\n"
                    "- <code>/canal listar</code> - Muestra tus canales.\n"
                    "- <code>/canal activar [nombre]</code> - Activa un canal.\n"
                    "- <code>/canal desactivar [nombre]</code> - Desactiva un canal.\n"
                    "- <code>/canal [nombre] [mensaje]</code> - Habla por un canal.",
                    parse_mode="HTML"
                )
                return

            subcommand = args[0].lower()

            # --- Enrutamiento de subcomandos ---
            if subcommand == "listar":
                await self._list_channels(character, session, message)

            elif subcommand in ["activar", "desactivar"]:
                if len(args) < 2:
                    await message.answer(f"Uso: /canal {subcommand} [nombre_canal]")
                    return
                channel_key = args[1].lower()
                await self._toggle_channel(character, session, message, subcommand, channel_key)

            else: # Si no es un subcomando, se asume que es el nombre de un canal para hablar.
                channel_key = subcommand
                text = " ".join(args[1:])
                if not text:
                    await message.answer(f"Uso: /canal {channel_key} [mensaje]")
                    return
                await self._speak_on_channel(character, session, message, channel_key, text)

        except Exception:
            await message.answer("❌ Ocurrió un error al procesar tu comando de canal.")
            logging.exception(f"Fallo al ejecutar /canal para {character.name}")

# Exportamos la lista de comandos. Ahora solo contiene una instancia del comando unificado.
CHANNEL_COMMANDS = [
    CmdCanal(),
]