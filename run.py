import logging
import sys
from pathlib import Path

# --- INICIO DE LA SOLUCIÓN INFALIBLE ---
# 1. Obtiene la ruta absoluta del archivo actual (run.py)
# 2. Sube un nivel para obtener la ruta raíz del proyecto (la carpeta 'runegram')
# 3. Añade esta ruta raíz a la lista de rutas de Python.
# Ahora, Python siempre sabrá buscar desde 'runegram/' para cualquier importación.
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))
# --- FIN DE LA SOLUCIÓN INFALIBLE ---

from aiogram import executor

# Ahora estas importaciones funcionarán sin ninguna duda
from src.bot.dispatcher import dp
from src import handlers

async def on_startup(dispatcher):
    logging.info("Bot iniciando...")

async def on_shutdown(dispatcher):
    logging.warning("Bot deteniéndose...")

def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

if __name__ == "__main__":
    main()