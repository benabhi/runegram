# src/bot/dispatcher.py
"""
Módulo para la Instanciación del Dispatcher de Aiogram.

Este archivo crea y configura la instancia global del `Dispatcher`, que es el
componente central de Aiogram para el procesamiento de actualizaciones (mensajes,
callbacks, etc.).

Responsabilidades:
1.  **Enrutamiento:** El `Dispatcher` (`dp`) es el objeto al que se registran
    todos los manejadores de mensajes (handlers). Se encarga de decidir qué
    función debe procesar cada mensaje entrante.
2.  **Gestión de Estados (FSM):** Configura el almacenamiento de estados finitos
    (Finite State Machine), que permite crear conversaciones de varios pasos
    (ej: creación de personaje, menús interactivos).
"""

from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from src.config import settings
from src.bot.bot import bot

# 1. Configuración del Almacenamiento de Estados (FSM - Finite State Machine)
# Se utiliza Redis (`RedisStorage2`) como backend para almacenar el estado de
# la conversación de cada usuario. Esto es esencial para funcionalidades
# de varios pasos, como la creación de personajes.
#
# `pool_size` se establece explícitamente para evitar el error 'Too many connections'
# que puede ocurrir si muchos usuarios interactúan con el bot simultáneamente.
storage = RedisStorage2(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    pool_size=20,
)

# 2. Creación de la Instancia del Dispatcher
# Se crea una instancia única del `Dispatcher` para toda la aplicación,
# vinculándola con la instancia del `bot` y el `storage` configurado.
dp = Dispatcher(bot, storage=storage)