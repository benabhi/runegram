# commands/command.py
"""
Módulo que define la Clase Base para todos los Comandos.

Este archivo contiene la clase `Command`, que actúa como una plantilla o "contrato"
para todos los comandos del juego. Cada comando, ya sea de jugador o de administrador,
debe heredar de esta clase.

Esto asegura que todos los comandos tengan una estructura consistente y puedan ser
manejados de manera uniforme por el dispatcher principal.
"""

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.character import Character

class Command:
    """
    Clase base abstracta para todos los comandos del juego.

    Atributos:
        names (list[str]): Una lista de alias que pueden invocar este comando.
                           El primer nombre de la lista se considera el principal.
        lock (str): Un string de permisos que el `permission_service` evaluará
                    para determinar si el personaje puede ejecutar el comando.
        description (str): Una breve descripción del propósito del comando, utilizada
                           para actualizar la lista de comandos en el cliente de Telegram.
    """
    lock: str = ""
    description: str = "Un comando sin descripción."

    def __init__(self, names: list[str] = None, description: str = None):
        """
        Inicializador que permite la creación de instancias de comandos
        con alias y descripciones dinámicas.

        Esto es especialmente útil para crear múltiples comandos a partir de una
        sola clase, como los comandos de movimiento (`/norte`, `/sur`, etc.).

        Args:
            names (list[str], optional): La lista de alias para esta instancia del comando.
                                         Si no se proporciona, se usa el atributo de clase.
            description (str, optional): La descripción para esta instancia del comando.
                                         Si no se proporciona, se usa el atributo de clase.
        """
        if names:
            self.names = names
        elif not hasattr(self, 'names'):
            self.names = []

        if description:
            self.description = description
        elif not hasattr(self, 'description'):
            # Asegura que siempre haya una descripción por defecto.
            self.description = "Un comando sin descripción."

    async def execute(
        self,
        character: Character,
        session: AsyncSession,
        message: types.Message,
        args: list[str]
    ):
        """
        El método principal que se ejecuta cuando se llama al comando.

        Este método debe ser sobrescrito por cada clase de comando hija.

        Args:
            character (Character): El objeto del personaje que ejecuta el comando,
                                   precargado con todas sus relaciones.
            session (AsyncSession): La sesión de base de datos activa para esta
                                    interacción.
            message (types.Message): El objeto de mensaje de Aiogram que contiene
                                     el texto original, el ID del chat, etc.
            args (list[str]): Una lista de los argumentos proporcionados por el
                              usuario después del nombre del comando.
        """
        # Este método está pensado para ser sobrescrito. Si una subclase no lo
        # implementa, lanzar un NotImplementedError es una buena práctica para
        # detectar errores durante el desarrollo.
        raise NotImplementedError