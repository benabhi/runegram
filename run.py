# run.py
import logging
import asyncio
import sys
from aiogram import executor

from src.bot.dispatcher import dp
from src.services import world_loader_service, ticker_service, online_service
from src.db import async_session_factory

import src.handlers

async def on_startup(dispatcher):
    logging.info("Bot iniciando...")

    ticker_service.initialize_scheduler()

    async with async_session_factory() as session:
        await world_loader_service.sync_world_from_prototypes(session)
        await ticker_service.load_and_schedule_all_tickers(session)

    # --- LÍNEA MODIFICADA ---
    # Añadimos la tarea global SIN pasarle ningún argumento.
    # La tarea se encargará de gestionar su propia sesión de base de datos.
    ticker_service.scheduler.add_job(
        online_service.check_for_newly_afk_players,
        'interval',
        seconds=60
    )
    logging.info("Ticker global para chequeo de AFK añadido.")

    logging.info("Ejecución de startup finalizada. El bot está en línea.")

async def on_shutdown(dispatcher):
    logging.warning("Bot deteniéndose...")
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