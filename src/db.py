# src/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings

# Creamos el motor de la base de datos asíncrono
async_engine = create_async_engine(
    settings.database_url,
    echo=False, # Ponlo en True para ver las queries SQL en la consola
)

# Creamos una fábrica de sesiones asíncronas
async_session_factory = async_sessionmaker(
    async_engine,
    expire_on_commit=False
)