# run.py

import logging
import sys
from pathlib import Path

# --- Añade la raíz del proyecto al path ---
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

# --- Importaciones de Aiogram ---
from aiogram import executor
from src.bot.dispatcher import dp


# --- LA LÍNEA MÁS IMPORTANTE ---
# Importamos nuestros paquetes de handlers explícitamente aquí.
# Esto fuerza a Python a ejecutar los archivos __init__.py de los handlers
# y registrar todos los decoradores @dp.message_handler en el orden correcto
# ANTES de que executor.start_polling se ejecute.
from src.handlers import admin_commands
from src.handlers import user_commands


async def on_startup(dispatcher):
    logging.info("Bot iniciando...")

async def on_shutdown(dispatcher):
    logging.warning("Bot deteniéndose...")

def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

if __name__ == "__main__":
    main()