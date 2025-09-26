from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from src.config import settings
from src.bot.bot import bot

storage = RedisStorage2(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)
dp = Dispatcher(bot, storage=storage)