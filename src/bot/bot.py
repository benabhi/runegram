from aiogram import Bot

from src.config import settings

bot = Bot(token=settings.bot_token.get_secret_value())