# run.py
"""
Punto de Entrada Principal de la Aplicación Runegram MUD.

Este script es el responsable de orquestar el arranque del bot. Sus tareas principales son:
1. Configurar el sistema de logging global para toda la aplicación.
2. Definir y registrar las funciones `on_startup` y `on_shutdown` que se ejecutarán
   al iniciar y detener el bot, respectivamente.
3. Iniciar el "polling" de Aiogram, que es el bucle principal que escucha los
   mensajes de Telegram.

Para ejecutar la aplicación, se llama a este script desde el `entrypoint.sh`
dentro del contenedor Docker.
"""

import logging
import asyncio
import sys
from aiogram import executor

from src.bot.dispatcher import dp
from src.services import world_loader_service, ticker_service, online_service
from src.db import async_session_factory

# Esta importación es crucial para que los manejadores de mensajes se registren.
import src.handlers

async def on_startup(dispatcher):
    """
    Se ejecuta una sola vez cuando el bot se inicia con éxito.
    Inicializa todos los sistemas principales del juego.
    """
    logging.info("Iniciando secuencia de arranque del bot...")

    try:
        # 1. Inicia el scheduler. Es importante que se inicie antes de que cualquier
        #    otro servicio intente añadir tareas.
        ticker_service.initialize_scheduler()

        # 2. Crea una sesión de base de datos para las tareas de inicialización.
        async with async_session_factory() as session:
            # Sincroniza el mundo estático (salas, salidas) desde los archivos de prototipos.
            await world_loader_service.sync_world_from_prototypes(session)

            # Carga y programa los tickers de los objetos que ya existen en la base de datos.
            await ticker_service.load_and_schedule_all_tickers(session)

        # 3. Añade el ticker global que se ejecuta periódicamente para comprobar
        #    el estado de inactividad (AFK) de los jugadores.
        ticker_service.scheduler.add_job(
            online_service.check_for_newly_afk_players,
            'interval',
            seconds=60,
            id="global_afk_check",
            replace_existing=True
        )
        logging.info("Ticker global para chequeo de AFK añadido.")

        logging.info("✅ Secuencia de arranque finalizada. El bot está en línea.")

    except Exception:
        # Si algo falla catastróficamente durante el arranque, lo registramos
        # y detenemos la aplicación para evitar un estado inconsistente.
        logging.exception("❌ Error fatal durante la secuencia de arranque. El bot se detendrá.")
        # Obtenemos el bucle de eventos actual y lo detenemos.
        loop = asyncio.get_running_loop()
        loop.stop()


async def on_shutdown(dispatcher):
    """
    Se ejecuta una sola vez cuando el bot se detiene.
    Se asegura de que los servicios se apaguen de forma limpia.
    """
    logging.warning("Iniciando secuencia de apagado del bot...")
    if ticker_service.scheduler.running:
        ticker_service.scheduler.shutdown()
        logging.info("Scheduler detenido limpiamente.")
    logging.warning("Bot detenido.")


def main():
    """
    Configura el logging principal y arranca el bot.
    """
    # Configuración de logging para que todos los mensajes (INFO, WARNING, ERROR, etc.)
    # se muestren en la consola del contenedor Docker con un formato claro.
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s [%(levelname)s] - %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Inicia el bucle de Aiogram que escucha los mensajes de Telegram.
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == "__main__":
    main()