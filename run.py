# run.py
import logging
# Ya no necesitamos sys ni Path para esto

from aiogram import executor
from src.bot.dispatcher import dp

# Esta importación ahora funcionará gracias al PYTHONPATH de Docker
import src.handlers

async def on_startup(dispatcher):
    logging.info("Bot iniciando...")

async def on_shutdown(dispatcher):
    logging.warning("Bot deteniéndose...")

def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

if __name__ == "__main__":
    import sys # Lo necesitamos para el logging
    main()