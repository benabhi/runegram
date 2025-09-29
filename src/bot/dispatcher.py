# src/bot/dispatcher.py

from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from src.config import settings
from src.bot.bot import bot

# Creamos el almacenamiento de estados con la configuración de Redis
storage = RedisStorage2(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)

# Creamos la instancia principal del Dispatcher que se usará en todo el proyecto
dp = Dispatcher(bot, storage=storage)