# commands/player/dynamic_channels.py
"""
Módulo para la Generación Dinámica de Comandos de Canal.

Este archivo contiene la lógica para crear automáticamente los comandos de chat
(ej: /novato, /sistema) a partir de las definiciones en
`game_data/channel_prototypes.py`.

Esto sigue la filosofía "Data-Driven" del motor: para añadir un nuevo canal
de chat al juego, un diseñador solo necesita añadir una entrada al archivo
de prototipos (con `type: "CHAT"`), y este módulo se encargará de crear el
comando correspondiente, aplicando los permisos definidos en el `lock`.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character
from src.services import channel_service
from game_data.channel_prototypes import CHANNEL_PROTOTYPES

class CmdDynamicChannel(Command):
    """
    Clase de comando genérica para enviar un mensaje a un canal de chat.
    La instancia de esta clase sabe a qué canal pertenece por su nombre.
    """
    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            # El nombre principal del comando (ej: "novato") es la clave del canal.
            channel_key = self.names[0]

            if not args:
                await message.answer(f"Uso: /{channel_key} [mensaje]")
                return

            proto = CHANNEL_PROTOTYPES.get(channel_key)
            if not proto:
                # Salvaguarda en caso de inconsistencia entre el comando y los prototipos.
                await message.answer("Error: El canal para este comando ya no existe.")
                return

            # 1. Verificar si el jugador tiene el canal activado para recibir mensajes.
            settings = await channel_service.get_or_create_settings(session, character)
            if not await channel_service.is_channel_active(settings, channel_key):
                await message.answer(f"Tienes el canal '{channel_key}' desactivado. Actívalo con:\n/activarcanal {channel_key}")
                return

            # 2. Formatear y transmitir el mensaje a través del servicio.
            text = " ".join(args)
            channel_message = f"[{character.name}] {text}"
            await channel_service.broadcast_to_channel(session, channel_key, channel_message, exclude_character_id=character.id)

            # 3. Enviar una confirmación al propio jugador para que vea su mensaje.
            await message.answer(f"{proto['icon']} <b>{proto['name']}:</b> {channel_message}", parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al enviar tu mensaje al canal.")
            logging.exception(f"Fallo al ejecutar un comando de canal dinámico para {character.name}")

def generate_channel_commands() -> list[Command]:
    """
    Función "fábrica" que lee los prototipos de canal y genera una lista
    de instancias de `CmdDynamicChannel` para cada canal de tipo 'CHAT'.
    Asigna dinámicamente los permisos (locks) definidos en el prototipo.
    """
    commands = []
    for key, proto in CHANNEL_PROTOTYPES.items():
        # Solo se crean comandos para los canales que están explícitamente marcados como CHAT.
        if proto.get("type") == "CHAT":
            instance = CmdDynamicChannel(
                names=[key],
                description=f"Envía un mensaje por el canal {proto['name']}."
            )
            # Asignamos el lock del prototipo al atributo de la instancia del comando.
            # Si el prototipo no tiene un lock, se asigna una cadena vacía (sin restricciones).
            instance.lock = proto.get("lock", "")
            commands.append(instance)
    return commands

# Exportamos la lista de comandos generados dinámicamente.
# El dispatcher importará esta lista.
DYNAMIC_CHANNEL_COMMANDS = generate_channel_commands()