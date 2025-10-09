# commands/admin/building.py
"""
Módulo de Comandos Administrativos para la Generación de Entidades.

Este archivo contiene los comandos que permiten a los administradores "generar"
o "invocar" (`spawn`) entidades en el mundo a partir de sus prototipos
definidos en `game_data`.

Estos comandos no se usan para construir el mundo estático (eso lo hace el
`world_loader_service`), sino para añadir contenido dinámico durante el juego,
como objetos para un evento o PNJ para una misión.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models.character import Character
from src.services import item_service, narrative_service
from game_data.item_prototypes import ITEM_PROTOTYPES

class CmdGenerarObjeto(Command):
    """
    Comando para que un administrador cree una instancia de un objeto
    a partir de un prototipo y la coloque en la sala actual.
    """
    names = ["generarobjeto", "genobj"]
    lock = "rol(ADMIN)"  # Solo usuarios con rol ADMIN o superior pueden usarlo.
    description = "Genera un objeto en la sala a partir de su clave de prototipo."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        # Validación de entrada
        if not args:
            await message.answer("Uso: /generarobjeto [key_del_prototipo]")
            return

        item_key = args[0].lower()

        try:
            # Llama al servicio para crear la instancia del objeto en la base de datos.
            item = await item_service.spawn_item_in_room(session, character.room_id, item_key)

            # Obtenemos el nombre "bonito" del prototipo para el mensaje de confirmación.
            item_name = ITEM_PROTOTYPES.get(item.key, {}).get("name", "un objeto desconocido")

            # Mensaje al admin
            await message.answer(f"✅ Objeto '{item_name}' generado en la sala actual.")

            # Mensaje social a la sala (broadcaster_service filtra automáticamente jugadores desconectados)
            from src.services import broadcaster_service
            narrative_message = narrative_service.get_random_narrative(
                "item_spawn",
                item_name=item_name
            )
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=character.room_id,
                message_text=narrative_message,
                exclude_character_id=None  # Todos los jugadores online lo ven, incluyendo el admin
            )

        except ValueError as e:
            # Este error se lanza desde `item_service` si la `item_key` no existe.
            await message.answer(f"❌ Error: {e}")
        except Exception:
            # Captura cualquier otro error inesperado durante el proceso de creación.
            await message.answer("❌ Ocurrió un error inesperado al generar el objeto.")
            logging.exception(f"Fallo al ejecutar /generarobjeto con la clave '{item_key}'")

class CmdDestruirObjeto(Command):
    """
    Comando para que un administrador elimine permanentemente una instancia de objeto
    del juego especificando su ID.
    """
    names = ["destruirobjeto", "delobj"]
    lock = "rol(ADMIN)"  # Solo usuarios con rol ADMIN o superior pueden usarlo.
    description = "Elimina permanentemente un objeto del juego usando su ID."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        # Validación de entrada
        if not args:
            await message.answer("Uso: /destruirobjeto [ID_del_objeto]\nEjemplo: /destruirobjeto 5")
            return

        try:
            item_id = int(args[0])
        except ValueError:
            await message.answer("❌ El ID del objeto debe ser un número válido.")
            return

        try:
            # Llama al servicio para eliminar el objeto de la base de datos.
            deleted_item = await item_service.delete_item(session, item_id)

            # Obtenemos el nombre del objeto eliminado para el mensaje de confirmación.
            item_name = deleted_item.get_name()

            # Mensaje al admin
            await message.answer(f"✅ Objeto '{item_name}' (ID: {item_id}) eliminado permanentemente.")

            # Notificaciones sociales según la ubicación del objeto
            from src.services import broadcaster_service

            # Caso 1: El objeto estaba en una sala
            if deleted_item.room_id:
                narrative_message = narrative_service.get_random_narrative(
                    "item_destroy_room",
                    item_name=item_name
                )
                await broadcaster_service.send_message_to_room(
                    session=session,
                    room_id=deleted_item.room_id,
                    message_text=narrative_message,
                    exclude_character_id=None  # Todos los jugadores online lo ven
                )

            # Caso 2: El objeto estaba en el inventario de un personaje
            elif deleted_item.character_id:
                # Cargar el personaje dueño manualmente (delete_item no precarga relaciones)
                from sqlalchemy import select
                from sqlalchemy.orm import selectinload
                from src.models import Character

                owner_query = (
                    select(Character)
                    .where(Character.id == deleted_item.character_id)
                    .options(selectinload(Character.account))
                )
                owner_result = await session.execute(owner_query)
                owner = owner_result.scalar_one_or_none()

                if owner:
                    narrative_message_private = narrative_service.get_random_narrative(
                        "item_destroy_inventory",
                        item_name=item_name
                    )
                    await broadcaster_service.send_message_to_character(
                        character=owner,
                        message_text=narrative_message_private
                    )

                    # Broadcast a la sala donde está el dueño
                    if owner.room_id:
                        narrative_message_room = narrative_service.get_random_narrative(
                            "item_destroy_room",
                            item_name=item_name
                        )
                        await broadcaster_service.send_message_to_room(
                            session=session,
                            room_id=owner.room_id,
                            message_text=narrative_message_room,
                            exclude_character_id=owner.id  # El dueño ya recibió mensaje privado
                        )

            # Caso 3: El objeto estaba dentro de un contenedor
            # No enviamos notificación social (los jugadores no ven directamente dentro de contenedores)

        except ValueError as e:
            # Este error se lanza desde `item_service` si el ID no existe.
            await message.answer(f"❌ Error: {e}")
        except Exception:
            # Captura cualquier otro error inesperado durante el proceso de eliminación.
            await message.answer("❌ Ocurrió un error inesperado al eliminar el objeto.")
            logging.exception(f"Fallo al ejecutar /destruirobjeto con el ID '{args[0]}'")

# Exportamos la lista de comandos de este módulo.
SPAWN_COMMANDS = [
    CmdGenerarObjeto(),
    CmdDestruirObjeto(),
]