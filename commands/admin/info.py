# commands/admin/info.py
"""
Módulo de Comandos Administrativos de Información.

Este archivo contiene comandos diseñados para que los administradores puedan
consultar el estado interno del juego. Son herramientas de solo lectura
que ayudan a supervisar, depurar y obtener una visión general del mundo
sin modificarlo.

Ejemplos futuros podrían incluir: /donde [jugador], /infoobjeto [id], etc.
"""

import logging
from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character, Room

class CmdListarSalas(Command):
    """
    Comando que muestra una lista de todas las salas existentes en el mundo,
    incluyendo su ID, su clave de prototipo y su nombre.
    """
    names = ["listarsalas", "lsalas"]
    lock = "rol(ADMIN)"
    description = "Muestra ID, Clave y Nombre de todas las salas del mundo."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        """Ejecuta la consulta y formatea la lista de salas."""
        try:
            # 1. Realizar la consulta a la base de datos para obtener todas las salas.
            # Se ordenan por ID para una visualización consistente.
            result = await session.execute(select(Room).order_by(Room.id))
            all_rooms = result.scalars().all()

            if not all_rooms:
                await message.answer("No se encontraron salas en la base de datos.")
                return

            # 2. Construir el mensaje de respuesta línea por línea.
            response_lines = ["<b>Lista de Salas del Mundo:</b>"]
            for room in all_rooms:
                # El formato con `<` alinea el texto a la izquierda, rellenando con espacios.
                response_lines.append(f"ID: {room.id:<4} | Key: {room.key:<20} | Nombre: {room.name}")

            body = "\n".join(response_lines)

            # 3. Envolver el cuerpo completo en una etiqueta <pre> para asegurar
            #    un formato de monoespaciado y una alineación perfecta de las columnas.
            response_text = f"<pre>{body}</pre>"

            await message.answer(response_text, parse_mode="HTML")

        except Exception:
            # Captura cualquier error inesperado durante la consulta a la base de datos.
            await message.answer("❌ Ocurrió un error al intentar listar las salas.")
            logging.exception("Fallo al ejecutar /listarsalas")

# Exportamos la lista de comandos de este módulo para que el dispatcher pueda importarla.
INFO_COMMANDS = [
    CmdListarSalas(),
]