# src/bot/bot.py
"""
Módulo para la Instanciación del Objeto Bot de Aiogram.

Este archivo tiene una única y simple responsabilidad: crear una instancia
global del objeto `Bot` de Aiogram.

Centralizar la creación de esta instancia aquí permite que cualquier otro
módulo en la aplicación (como los servicios) pueda importarla para interactuar
directamente con la API de Telegram (por ejemplo, para enviar mensajes
proactivos fuera del flujo normal de un comando).
"""

from aiogram import Bot

from src.config import settings

# Se crea una instancia única del Bot para toda la aplicación.
# El token se lee de forma segura desde el objeto de configuración `settings`,
# que a su vez lo carga desde las variables de entorno.
# `settings.bot_token.get_secret_value()` es la forma correcta de acceder
# al valor de un `SecretStr` de Pydantic.
bot = Bot(token=settings.bot_token.get_secret_value())