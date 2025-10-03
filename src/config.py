# src/config.py
"""
Módulo de Configuración Centralizado.

Este archivo define la clase `Settings` que utiliza Pydantic para cargar, validar
y gestionar todas las variables de entorno necesarias para la aplicación.

Pydantic se encarga de:
1. Leer las variables desde un archivo `.env`.
2. Validar que las variables existan y tengan el tipo de dato correcto (ej: int, str).
3. Proveer un objeto `settings` único y fuertemente tipado que puede ser importado
   y utilizado en cualquier parte del proyecto.

Esto evita la dispersión de `os.getenv()` por el código y asegura que la aplicación
no arranque si falta una configuración crítica.
"""

from pydantic import BaseSettings, SecretStr

class Settings(BaseSettings):
    """
    Define y carga todas las variables de entorno de la aplicación.
    """
    # Telegram
    bot_token: SecretStr

    # El ID de Telegram del usuario que tendrá el rol de Superadmin.
    # Este rol tiene todos los permisos y se asigna al arrancar la aplicación.
    superadmin_telegram_id: int

    # Database (PostgreSQL)
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    # Cache y Estados (Redis)
    redis_host: str
    redis_port: int
    redis_db: int

    # Display Limits - Límites de visualización para prevenir spam
    # Estos valores controlan cuántos items se muestran en listas antes de truncar
    max_room_items_display: int = 10  # Items mostrados en /mirar (sala)
    max_room_characters_display: int = 10  # Personajes mostrados en /mirar (sala)
    max_inventory_display: int = 15  # Items mostrados en /inventario
    max_container_display: int = 15  # Items mostrados al mirar/abrir contenedor
    max_who_display: int = 20  # Jugadores mostrados en /quien

    @property
    def database_url(self) -> str:
        """
        Genera la URL de conexión a la base de datos para el motor ASÍNCRONO.
        Utiliza el driver 'asyncpg', que es el principal para la aplicación.
        """
        return (
            f"postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """
        Genera la URL de conexión a la base de datos para operaciones SÍNCRONAS.
        Utiliza el driver 'psycopg2'. Su uso principal es para componentes que no
        son compatibles con asyncio, como el `SQLAlchemyJobStore` de APScheduler.
        """
        return (
            f"postgresql+psycopg2://"
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        """
        Configuración interna de Pydantic para indicarle cómo cargar las variables.
        """
        # Nombre del archivo del que se leerán las variables de entorno.
        env_file = '.env'
        # Codificación del archivo .env.
        env_file_encoding = 'utf-8'

# Creamos una instancia única de la configuración que será importada
# por el resto de la aplicación.
settings = Settings()