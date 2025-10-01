# commands/admin/management.py
"""
Módulo de Comandos Administrativos para la Gestión del Juego.

Este archivo contiene comandos de alto nivel que permiten a los administradores
modificar el estado persistente de las entidades del juego, como cambiar el
rol de un jugador.

Estos comandos son generalmente restrictivos y solo accesibles para los roles
más altos, como SUPERADMIN.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from commands.command import Command
from src.models import Character, Account
from src.services.permission_service import ROLE_HIERARCHY

class CmdAsignarRol(Command):
    """
    Comando de Superadmin para cambiar el rol de la cuenta de un personaje.
    """
    names = ["asignarrol"]
    lock = "rol(SUPERADMIN)"
    description = "Cambia el rol de un jugador. Uso: /asignarrol <nombre> <rol>"

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        if len(args) != 2:
            roles = ", ".join(ROLE_HIERARCHY.keys())
            await message.answer(f"Uso: /asignarrol <nombre_personaje> <rol>\nRoles disponibles: {roles}")
            return

        target_name, new_role = args
        new_role = new_role.upper()

        if new_role not in ROLE_HIERARCHY:
            roles = ", ".join(ROLE_HIERARCHY.keys())
            await message.answer(f"El rol '{new_role}' no es válido. Roles disponibles: {roles}")
            return

        try:
            # 1. Buscar al personaje por nombre.
            query = select(Character).where(Character.name.ilike(target_name))
            result = await session.execute(query)
            target_char = result.scalar_one_or_none()

            if not target_char:
                await message.answer(f"No se encontró un personaje con el nombre '{target_name}'.")
                return

            # 2. Obtener su cuenta.
            target_account = await session.get(Account, target_char.account_id)
            if not target_account:
                # Esto no debería ocurrir si la base de datos es consistente.
                await message.answer("Error: El personaje encontrado no tiene una cuenta asociada.")
                return

            # 3. Validar jerarquía: no se puede asignar un rol igual o superior al propio.
            user_level = ROLE_HIERARCHY.get(character.account.role.upper(), 0)
            new_role_level = ROLE_HIERARCHY.get(new_role, 0)

            if new_role_level >= user_level and character.id != target_char.id:
                 await message.answer("No puedes asignar un rol igual o superior a tu propio rango.")
                 return

            # 4. Actualizar el rol y guardar en la base de datos.
            old_role = target_account.role
            target_account.role = new_role
            await session.commit()

            await message.answer(f"✅ Se ha cambiado el rol de {target_char.name} de '{old_role}' a '{new_role}'.")

        except Exception:
            await message.answer("❌ Ocurrió un error al intentar asignar el rol.")
            logging.exception(f"Fallo al ejecutar /asignarrol para '{target_name}'")

# Exportamos la lista de comandos de este módulo.
MANAGEMENT_COMMANDS = [
    CmdAsignarRol(),
]