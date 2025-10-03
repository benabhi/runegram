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
from sqlalchemy import select

from src.bot.dispatcher import dp
from src.services import world_loader_service, pulse_service, online_service, validation_service
from src.db import async_session_factory
from src.config import settings
from src.models import Account

# Esta importación es crucial para que los manejadores de mensajes se registren.
import src.handlers

async def _ensure_superadmin_exists(session):
    """
    Verifica que la cuenta del Superadmin (definida en .env) exista y tenga
    el rol correcto. La crea o actualiza si es necesario.

    Esta función de "autocorrección" se ejecuta en cada arranque para garantizar
    que el Superadmin siempre esté configurado correctamente, eliminando la
    necesidad de sembrar datos frágiles en las migraciones.
    """
    superadmin_id = settings.superadmin_telegram_id
    if not superadmin_id:
        logging.warning("No se ha definido un SUPERADMIN_TELEGRAM_ID en el archivo .env.")
        return

    result = await session.execute(select(Account).where(Account.telegram_id == superadmin_id))
    superadmin_account = result.scalar_one_or_none()

    if not superadmin_account:
        logging.info(f"Creando cuenta de Superadmin para el telegram_id: {superadmin_id}")
        superadmin_account = Account(telegram_id=superadmin_id, role="SUPERADMIN")
        session.add(superadmin_account)
        await session.commit()
    elif superadmin_account.role != "SUPERADMIN":
        logging.info(f"Actualizando cuenta {superadmin_id} al rol de Superadmin.")
        superadmin_account.role = "SUPERADMIN"
        await session.commit()
    else:
        logging.info("Cuenta de Superadmin verificada.")


async def on_startup(dispatcher):
    """
    Se ejecuta una sola vez cuando el bot se inicia con éxito.
    Inicializa todos los sistemas principales del juego.
    """
    logging.info("Iniciando secuencia de arranque del bot...")

    try:
        # 0. VALIDACIONES CRÍTICAS: Ejecutar antes de cualquier inicialización.
        #    Si hay errores de configuración, el bot no debe arrancar.
        validation_service.validate_all()

        # 1. Inicia el sistema de pulse global.
        pulse_service.initialize_pulse_system()

        # 2. Crea una sesión de base de datos para las tareas de inicialización.
        async with async_session_factory() as session:
            # Asegura que la cuenta del Superadmin exista y tenga el rol correcto.
            await _ensure_superadmin_exists(session)

            # Sincroniza el mundo estático (salas, salidas) desde los archivos de prototipos.
            await world_loader_service.sync_world_from_prototypes(session)

        # 3. Añade el job para el chequeo de inactividad.
        pulse_service.scheduler.add_job(
            online_service.check_for_newly_afk_players,
            'interval',
            seconds=60,
            id="global_afk_check",
            replace_existing=True
        )
        logging.info("Job para chequeo de AFK añadido.")

        logging.info("✅ Secuencia de arranque finalizada. El bot está en línea.")

    except Exception:
        # Si algo falla catastróficamente durante el arranque, lo registramos
        # y detenemos la aplicación para evitar un estado inconsistente.
        logging.exception("❌ Error fatal durante la secuencia de arranque. El bot se detendrá.")
        loop = asyncio.get_running_loop()
        loop.stop()


async def on_shutdown(dispatcher):
    """
    Se ejecuta una sola vez cuando el bot se detiene.
    Se asegura de que los servicios se apaguen de forma limpia.
    """
    logging.warning("Iniciando secuencia de apagado del bot...")
    pulse_service.shutdown_pulse_system()
    logging.warning("Bot detenido.")


def main():
    """
    Configura el logging principal y arranca el bot.
    """
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s [%(levelname)s] - %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == "__main__":
    main()