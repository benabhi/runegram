# commands/admin/diagnostics.py
"""
Módulo de Comandos Administrativos para Diagnóstico e Inspección.

Contiene herramientas para que los administradores puedan inspeccionar el estado
detallado de las entidades del juego, como personajes, objetos y salas.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from commands.command import Command
from src.models import Character, Item, Room
from src.services import validation_service

class CmdExamineCharacter(Command):
    """
    Comando para obtener información detallada sobre un personaje.
    """
    names = ["examinarpersonaje", "exchar"]
    lock = "rol(ADMIN)"
    description = "Muestra información detallada de un personaje. Uso: /exchar [nombre o ID]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            await message.answer("Uso: /examinarpersonaje [nombre o ID del personaje]")
            return

        target_string = " ".join(args)

        try:
            target_char = None
            try:
                # Buscar por ID
                char_id = int(target_string)
                target_char = await session.get(Character, char_id)
            except ValueError:
                # Buscar por nombre si no es un ID
                query = select(Character).where(Character.name.ilike(f"%{target_string}%"))
                result = await session.execute(query)
                target_char = result.scalar_one_or_none()

            if not target_char:
                await message.answer(f"No se encontró ningún personaje que coincida con '{target_string}'.")
                return

            # Cargar todas las relaciones necesarias para mostrar la información completa
            query_full = (
                select(Character)
                .where(Character.id == target_char.id)
                .options(
                    selectinload(Character.account),
                    selectinload(Character.room),
                    selectinload(Character.items)
                )
            )
            result_full = await session.execute(query_full)
            full_char = result_full.scalar_one()

            lines = [
                f"<b>--- PERSONAJE: {full_char.name} ---</b>",
                f"<b>ID:</b> {full_char.id}",
                f"<b>Cuenta ID:</b> {full_char.account_id} (Rol: {full_char.account.role})",
                f"<b>Sala Actual:</b> {full_char.room.name} (ID: {full_char.room_id})",
                f"<b>CommandSets Base:</b> {', '.join(full_char.command_sets)}",
            ]
            if full_char.items:
                lines.append("<b>Inventario:</b>")
                for item in full_char.items:
                    lines.append(f"  - {item.get_name()} (ID: {item.id}, Key: {item.key})")
            else:
                lines.append("<b>Inventario:</b> Vacío")

            body = '\n'.join(lines)
            await message.answer(f"<pre>{body}</pre>", parse_mode="HTML")

        except Exception:
            await message.answer("❌ Ocurrió un error al examinar el personaje.")
            logging.exception(f"Fallo al ejecutar /examinarpersonaje para '{target_string}'")


class CmdExamineItem(Command):
    """
    Comando para obtener información detallada sobre una instancia de objeto.
    """
    names = ["examinarobjeto", "exobj"]
    lock = "rol(ADMIN)"
    description = "Muestra información detallada de un objeto. Uso: /exobj [ID]"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if not args:
            await message.answer("Uso: /examinarobjeto [ID del objeto]")
            return

        try:
            item_id = int(args[0])
            target_item = await session.get(Item, item_id, options=[selectinload("*")])

            if not target_item:
                await message.answer(f"No se encontró ningún objeto con el ID '{item_id}'.")
                return

            lines = [
                f"<b>--- OBJETO: {target_item.get_name()} ---</b>",
                f"<b>ID de Instancia:</b> {target_item.id}",
                f"<b>Clave de Prototipo:</b> {target_item.key}",
            ]
            if target_item.room:
                lines.append(f"<b>Ubicación:</b> Sala '{target_item.room.name}' (ID: {target_item.room_id})")
            elif target_item.character:
                lines.append(f"<b>Ubicación:</b> Inventario de '{target_item.character.name}' (ID: {target_item.character_id})")
            else:
                lines.append("<b>Ubicación:</b> En el limbo (ninguna sala/personaje)")

            lines.append(f"<b>Nombre Overr.:</b> {target_item.name_override or 'N/A'}")
            lines.append(f"<b>Desc. Overr.:</b> {target_item.description_override or 'N/A'}")

            body = '\n'.join(lines)
            await message.answer(f"<pre>{body}</pre>", parse_mode="HTML")

        except ValueError:
            await message.answer("El ID del objeto debe ser un número.")
        except Exception:
            await message.answer("❌ Ocurrió un error al examinar el objeto.")
            logging.exception(f"Fallo al ejecutar /examinarobjeto para '{args[0]}'")

class CmdValidate(Command):
    """
    Comando que muestra un reporte de validación de integridad del sistema.
    Útil para diagnosticar conflictos de aliases, keys duplicadas, etc.
    """
    names = ["validar", "reportevalidacion"]
    lock = "rol(ADMIN)"
    description = "Muestra un reporte de validación de integridad del sistema."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            report = validation_service.get_validation_report()
            await message.answer(f"<pre>{report}</pre>", parse_mode="HTML")
        except Exception:
            await message.answer("❌ Ocurrió un error al generar el reporte de validación.")
            logging.exception("Fallo al ejecutar /validar")


# Exportamos la lista de comandos de este módulo.
DIAGNOSTICS_COMMANDS = [
    CmdExamineCharacter(),
    CmdExamineItem(),
    CmdValidate(),
]