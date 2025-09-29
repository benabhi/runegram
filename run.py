# run.py
import logging
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

from aiogram import executor
from src.bot.dispatcher import dp

# --- IMPORTACIÓN ÚNICA Y FINAL ---
# Esta única línea cargará transitivamente handlers -> player -> dispatcher,
# registrando nuestro único handler en 'dp'.
import src.handlers

async def on_startup(dispatcher):
    logging.info("Bot iniciando...")

async def on_shutdown(dispatcher):
    logging.warning("Bot deteniéndose...")

def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

if __name__ == "__main__":
    main()