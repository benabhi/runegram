# commands/player/settings.py
"""
Módulo de Comandos para la Configuración del Personaje.

Este archivo contiene los comandos que permiten a los jugadores personalizar
su experiencia de juego, como ajustar las notificaciones, los colores (en el
futuro), u otras preferencias.

Actualmente, sirve como punto de entrada para la gestión de canales, pero
está diseñado para albergar más comandos de configuración a medida que el
juego crezca.
"""

import logging
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from commands.command import Command
from src.models import Character

class CmdConfig(Command):
    """
    Comando principal para que un jugador acceda a las opciones de configuración.
    Actualmente, muestra una ayuda contextual sobre cómo gestionar los canales.
    """
    names = ["config", "opciones"]
    description = "Muestra las opciones de configuración disponibles."

    async def execute(self, character: Character, session: AsyncSession, message: types.Message, args: list[str]):
        try:
            help_text = (
                "<pre>⚙️ <b>CONFIGURACIÓN DE RUNEGRAM</b>\n"
                "─────────────────────────────\n"
                "Aquí podrás ajustar tus preferencias de juego.\n\n"
                "<b>Gestión de Canales:</b>\n"
                "    - Usa <code>/canales</code> para ver una lista de todos los canales y su estado.\n"
                "    - Usa <code>/activarcanal [nombre]</code> para suscribirte a un canal.\n"
                "    - Usa <code>/desactivarcanal [nombre]</code> para cancelar tu suscripción.</pre>"
            )
            await message.answer(help_text, parse_mode="HTML")
        except Exception:
            await message.answer("❌ Ocurrió un error al mostrar las opciones de configuración.")
            logging.exception(f"Fallo al ejecutar /config para {character.name}")

# Exportamos la lista de comandos de este módulo.
SETTINGS_COMMANDS = [
    CmdConfig(),
]