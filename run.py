# run.py
import logging
import asyncio
import sys
from aiogram import executor

from src.bot.dispatcher import dp
# Importamos todos los servicios necesarios para el arranque
from src.services import world_loader_service, ticker_service
from src.db import async_session_factory

import src.handlers

async def on_startup(dispatcher):
    logging.info("Bot iniciando...")

    # Paso 1: Iniciamos el scheduler (el motor de tareas programadas)
    ticker_service.initialize_scheduler()

    async with async_session_factory() as session:
        # Sincronizamos el mundo estático (salas y salidas)
        await world_loader_service.sync_world_from_prototypes(session)

        # Paso 2: Cargamos los tickers de entidades que ya existen en la BD
        await ticker_service.load_and_schedule_all_tickers(session)

    logging.info("Ejecución de startup finalizada. El bot está en línea.")

async def on_shutdown(dispatcher):
    logging.warning("Bot deteniéndose...")
    # Es una buena práctica apagar el scheduler de forma limpia
    ticker_service.scheduler.shutdown()

def main():
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s [%(levelname)s] - %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)

if __name__ == "__main__":
    main()