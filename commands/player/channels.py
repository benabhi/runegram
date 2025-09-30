# commands/player/channels.py
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from commands.command import Command
from src.models import Character
from src.services import channel_service
from game_data.channel_prototypes import CHANNEL_PROTOTYPES

class CmdChannel(Command):
    names = ["canal"]
    description = "Activa o desactiva un canal. Uso: /canal [activar|desactivar] [nombre]."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args or len(args) < 2 or args[0].lower() not in ["activar", "desactivar"]:
            await message.answer("Uso: /canal [activar|desactivar] [nombre_canal]")
            return

        action = args[0].lower()
        channel_key = args[1].lower()

        try:
            await channel_service.set_channel_status(session, character, channel_key, activate=(action == "activar"))
            await message.answer(f"✅ Has {action}do el canal '{channel_key}'.")
        except ValueError as e:
            await message.answer(f"❌ Error: {e}")

class CmdChannels(Command):
    names = ["canales"]
    description = "Muestra los canales disponibles y su estado (activado/desactivado)."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        settings = await channel_service.get_or_create_settings(session, character)
        user_channels = settings.active_channels.get("active_channels", [])

        response = ["<b>Estado de tus Canales:</b>"]
        for key, proto in CHANNEL_PROTOTYPES.items():
            status = "✅ Activado" if key in user_channels else "❌ Desactivado"
            response.append(f"- <b>{proto['name']}</b> ({key}): {status}\n  <i>{proto['description']}</i>")

        await message.answer("\n".join(response), parse_mode="HTML")


class CmdNovato(Command):
    names = ["novato"]
    lock = ""
    description = "Envía un mensaje por el canal de ayuda para novatos."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            return await message.answer("Uso: /novato [mensaje]")

        settings = await channel_service.get_or_create_settings(session, character)
        if not await channel_service.is_channel_active(settings, "novato"):
            return await message.answer("Tienes el canal 'novato' desactivado. Actívalo con:\n/canal activar novato")

        channel_message = f"[{character.name}] {' '.join(args)}"
        await channel_service.broadcast_to_channel(session, "novato", channel_message, exclude_character_id=character.id)
        # Confirmación para el que envía el mensaje
        await message.answer(f"📢 <b>Novato:</b> {channel_message}", parse_mode="HTML")

CHANNEL_COMMANDS = [
    CmdChannel(),
    CmdChannels(),
    CmdNovato(),
]