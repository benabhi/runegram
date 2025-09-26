# alembic/env.py

# --- INICIO DE LA CONFIGURACIÓN DEL PATH ---
# Añade el directorio raíz del proyecto al sys.path para que Python
# pueda encontrar nuestros módulos (como 'src').
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
# --- FIN DE LA CONFIGURACIÓN DEL PATH ---


import asyncio
from logging.config import fileConfig
from alembic import context

# Importaciones de SQLAlchemy
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# --- Importaciones de nuestro proyecto ---
# Ahora podemos importar la Base de nuestros modelos para la autogeneración
# y la configuración (settings) para obtener la URL de la base de datos.
from src.models import Base
from src.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line reads the ini file.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# --- INICIO DE LA CONFIGURACIÓN DINÁMICA DE LA URL DE LA BD ---
# Aquí sobrescribimos la URL de la base de datos que está en alembic.ini
# con la URL real y segura que se encuentra en nuestra configuración de la aplicación.
# Esto centraliza la configuración y evita exponer secretos.
config.set_main_option('sqlalchemy.url', settings.database_url)
# --- FIN DE LA CONFIGURACIÓN DINÁMICA DE LA URL DE LA BD ---


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    Función auxiliar que Alembic ejecutará de forma síncrona
    una vez que la conexión asíncrona se haya establecido.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Usamos create_async_engine para crear un motor asíncrono
    # a partir de la URL de nuestra configuración.
    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    # Usamos el motor para conectar de forma asíncrona
    async with connectable.connect() as connection:
        # Una vez conectados, configuramos el contexto de Alembic
        await connection.run_sync(do_run_migrations)

    # Limpiamos el motor al terminar
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())