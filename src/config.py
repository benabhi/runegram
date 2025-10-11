# src/config.py
"""
Módulo de Configuración Centralizado.

Este archivo define la clase `Settings` que utiliza Pydantic para cargar, validar
y gestionar todas las configuraciones de la aplicación desde dos fuentes:

1. `.env` - Credenciales sensibles (tokens, passwords)
2. `gameconfig.toml` - Configuración del juego (tiempos, límites, comportamiento)

Pydantic se encarga de:
1. Leer las variables desde `.env` y `gameconfig.toml`.
2. Validar que las variables existan y tengan el tipo de dato correcto (ej: int, str).
3. Proveer un objeto `settings` único y fuertemente tipado que puede ser importado
   y utilizado en cualquier parte del proyecto.

Esto evita la dispersión de configuraciones hardcodeadas por el código y asegura
que la aplicación no arranque si falta una configuración crítica.
"""

import toml
from datetime import timedelta
from pydantic import BaseSettings, SecretStr, validator

class Settings(BaseSettings):
    """
    Define y carga todas las configuraciones de la aplicación.
    Combina variables de entorno (.env) con configuración del juego (gameconfig.toml).
    """
    # ===============================
    # Configuraciones desde .env
    # ===============================

    # Telegram
    bot_token: SecretStr

    # El ID de Telegram del usuario que tendrá el rol de Superadmin.
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

    # ===============================
    # Configuraciones desde gameconfig.toml
    # ===============================

    # Sistema de Presencia (Online/Offline)
    online_threshold_minutes: int = 5
    online_last_seen_ttl_days: int = 7
    online_offline_notified_ttl_days: int = 1

    # Sistema de Pulse Global
    pulse_interval_seconds: int = 2

    # Paginación
    pagination_items_per_page: int = 30

    # Límites de Visualización
    display_limits_max_room_items: int = 10
    display_limits_max_room_characters: int = 10
    display_limits_max_inventory: int = 15
    display_limits_max_container: int = 15
    display_limits_max_who: int = 20

    # Sistema de Baneos y Moderación
    moderation_ban_appeal_channel: str = "moderacion"

    # Gameplay General
    gameplay_debug_mode: bool = False

    # ===============================
    # Propiedades Computadas
    # ===============================

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

    @property
    def online_threshold(self) -> timedelta:
        """Retorna el umbral de online como timedelta."""
        return timedelta(minutes=self.online_threshold_minutes)

    @property
    def last_seen_ttl(self) -> timedelta:
        """Retorna el TTL de last_seen como timedelta."""
        return timedelta(days=self.online_last_seen_ttl_days)

    @property
    def offline_notified_ttl(self) -> timedelta:
        """Retorna el TTL de offline_notified como timedelta."""
        return timedelta(days=self.online_offline_notified_ttl_days)

    class Config:
        """
        Configuración interna de Pydantic para indicarle cómo cargar las variables.
        """
        # Nombre del archivo del que se leerán las variables de entorno.
        env_file = '.env'
        # Codificación del archivo .env.
        env_file_encoding = 'utf-8'


# ===============================
# Carga de Configuración
# ===============================

def load_game_config():
    """
    Carga el archivo gameconfig.toml y retorna un dict con los valores aplanados.

    Esto permite que Pydantic los cargue como si fueran variables de entorno.
    """
    try:
        with open('gameconfig.toml', 'r', encoding='utf-8') as f:
            config = toml.load(f)

        # Aplanar la estructura TOML para Pydantic
        # [online] threshold_minutes -> online_threshold_minutes
        flat_config = {}
        for section, values in config.items():
            for key, value in values.items():
                flat_config[f"{section}_{key}"] = value

        return flat_config

    except FileNotFoundError:
        # Si no existe gameconfig.toml, usar valores por defecto
        # (ya definidos en la clase Settings)
        return {}


# Cargar configuración del juego desde TOML
_game_config = load_game_config()

# Creamos una instancia única de la configuración que será importada
# por el resto de la aplicación.
# Pydantic primero carga .env, luego sobrescribe con lo que pasemos como kwargs
settings = Settings(**_game_config)