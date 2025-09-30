# src/bot/dispatcher.py

from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from src.config import settings
from src.bot.bot import bot

# Creamos el almacenamiento de estados con la configuración de Redis.
#
# Se especifica explícitamente un 'pool_size' más grande para evitar
# el error 'redis.exceptions.ConnectionError: Too many connections'
# que ocurre cuando la aplicación recibe varios mensajes a la vez y
# agota el pequeño pool de conexiones por defecto.
storage = RedisStorage2(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    pool_size=20,  # Aumentamos el número de conexiones disponibles en el pool. 20 es un buen punto de partida.
)

# Creamos la instancia principal del Dispatcher que se usará en todo el proyecto
dp = Dispatcher(bot, storage=storage)