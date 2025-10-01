# commands/admin/diagnostics.py
"""
Módulo de Comandos Administrativos para Diagnóstico e Inspección.

Este archivo contiene herramientas potentes para que los Superadmins puedan
"mirar bajo el capó" del juego en tiempo real. Permiten inspeccionar el
estado detallado de cualquier entidad (personajes, objetos, salas) directamente
desde el juego.

Estos comandos son cruciales para la depuración de bugs, la verificación de
estados y la administración avanzada del mundo.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from commands.command import Command
from src.models import Character, Item, Room

async def _find_target(session: AsyncSession, target_string: str):
    """Función de ayuda para encontrar una entidad por su nombre o ID."""
    # Intentar buscar por ID numérico
    try:
        target_id = int(target_string)
        # Buscar personaje por ID
        char_by_id = await session.get(Character, target_id, options=[selectinload("*")])
        if char_by_id: return char_by_id

        # Buscar objeto por ID
        item_by_id = await session.get(Item, target_id, options=[selectinload("*")])
        if item_by_id: return item_by_id

        # Buscar sala por ID
        room_by_id = await session.get(Room, target_id, options=[selectinload("*")])
        if room_by_id: return room_by_id

    except ValueError:
        # Si no es un número, buscamos por nombre
        pass

    # Buscar personaje por nombre (insensible a mayúsculas)
    char_query = select(Character).where(Character.name.ilike(f"%{target_string}%"))
    char_res = await session.execute(char_query)
    character = char_res.scalar_one_or_none()
    if character: return character

    return None

class CmdExamine(Command):
    """
    Comando de Superadmin para obtener información detallada de cualquier entidad.
    """
    names = ["examinar", "ex"]
    lock = "rol(SUPERADMIN)"
    description = "Muestra información detallada de una entidad (jugador, objeto, sala)."

    def format_output(self, target) -> str:
        """Formatea la información de la entidad para mostrarla."""
        lines = []

        # --- Formateo para Personaje ---
        if isinstance(target, Character):
            lines.append(f"<b>--- Personaje: {target.name} ---</b>")
            lines.append(f"<b>ID:</b> {target.id}")
            lines.append(f"<b>Cuenta ID:</b> {target.account_id}")
            lines.append(f"<b>Sala Actual:</b> {target.room.name} (ID: {target.room_id})")
            lines.append(f"<b>CommandSets Base:</b> {', '.join(target.command_sets)}")
            if target.items:
                lines.append("<b>Inventario:</b>")
                for item in target.items:
                    lines.append(f"  - {item.get_name()} (ID: {item.id}, Key: {item.key})")
            else:
                lines.append("<b>Inventario:</b> Vacío")

        # --- Formateo para Objeto ---
        elif isinstance(target, Item):
            lines.append(f"<b>--- Objeto: {target.get_name()} ---</b>")
            lines.append(f"<b>ID de Instancia:</b> {target.id}")
            lines.append(f"<b>Clave de Prototipo:</b> {target.key}")
            if target.room:
                lines.append(f"<b>Ubicación:</b> Sala '{target.room.name}' (ID: {target.room_id})")
            elif target.character:
                lines.append(f"<b>Ubicación:</b> Inventario de '{target.character.name}' (ID: {target.character_id})")
            else:
                lines.append("<b>Ubicación:</b> En el limbo (ninguna sala/personaje)")
            lines.append(f"<b>Nombre Overr.:</b> {target.name_override or 'N/A'}")
            lines.append(f"<b>Desc. Overr.:</b> {target.description_override or 'N/A'}")

        # --- Formateo para Sala ---
        elif isinstance(target, Room):
            lines.append(f"<b>--- Sala: {target.name} ---</b>")
            lines.append(f"<b>ID:</b> {target.id}")
            lines.append(f"<b>Clave de Prototipo:</b> {target.key}")
            if target.items:
                lines.append("<b>Objetos en la sala:</b>")
                for item in target.items:
                    lines.append(f"  - {item.get_name()} (ID: {item.id}, Key: {item.key})")
            else:
                lines.append("<b>Objetos en la sala:</b> Ninguno")

        else:
            return "No se cómo examinar este tipo de entidad."

        # Primero unimos las líneas en una variable...
        body = '\n'.join(lines)
        # ... y luego usamos esa variable en la f-string.
        return f"<pre>{body}</pre>"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            await message.answer("Uso: /examinar [nombre o ID de entidad]")
            return

        target_string = " ".join(args)

        try:
            target = await _find_target(session, target_string)

            if not target:
                await message.answer(f"No se encontró ninguna entidad que coincida con '{target_string}'.")
                return

            # Cargar todas las relaciones necesarias para el formateo
            await session.refresh(target, attribute_names=['*'])

            response = self.format_output(target)
            await message.answer(response, parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al examinar la entidad.")
            logging.exception(f"Fallo al ejecutar /examinar para '{target_string}'")

# Exportamos la lista de comandos de este módulo.
DIAGNOSTICS_COMMANDS = [
    CmdExamine(),
]