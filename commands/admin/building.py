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
from src.services import item_service
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

            # Mensaje social a la sala
            from src.services import broadcaster_service
            await broadcaster_service.send_message_to_room(
                session=session,
                room_id=character.room_id,
                message_text=f"<i>{item_name.capitalize()} aparece de la nada.</i>",
                exclude_character_id=None  # Todos ven esto, incluyendo el admin
            )

        except ValueError as e:
            # Este error se lanza desde `item_service` si la `item_key` no existe.
            await message.answer(f"❌ Error: {e}")
        except Exception:
            # Captura cualquier otro error inesperado durante el proceso de creación.
            await message.answer("❌ Ocurrió un error inesperado al generar el objeto.")
            logging.exception(f"Fallo al ejecutar /generarobjeto con la clave '{item_key}'")

# Exportamos la lista de comandos de este módulo.
SPAWN_COMMANDS = [
    CmdGenerarObjeto(),
]