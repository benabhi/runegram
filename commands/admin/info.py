# commands/admin/info.py
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character, Room

class CmdListarSalas(Command):
    names = ["listarsalas", "lsalas"]
    lock = "rol(ADMINISTRADOR)"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        """Muestra una lista de todas las salas del juego con su ID, Key y Nombre."""

        result = await session.execute(select(Room).order_by(Room.id))
        all_rooms = result.scalars().all()

        if not all_rooms:
            return await message.answer("No se encontraron salas en la base de datos.")

        # Construimos el cuerpo del mensaje
        response_lines = ["<b>Lista de Salas del Mundo:</b>"]
        for room in all_rooms:
            # Ya no necesitamos <code> en cada línea, <pre> se encargará del formato
            response_lines.append(f"ID: {room.id:<4} | Key: {room.key:<20} | Nombre: {room.name}")

        body = "\n".join(response_lines)

        # Envolvemos el cuerpo completo en una etiqueta <pre>
        response_text = f"<pre>{body}</pre>"

        # Usamos parse_mode HTML para que Telegram interprete las etiquetas
        await message.answer(response_text, parse_mode="HTML")

# Exportamos el nuevo set de comandos de información
INFO_COMMANDS = [
    CmdListarSalas(),
]