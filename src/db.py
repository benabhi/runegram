# src/db.py
"""
Módulo de Configuración de la Base de Datos.

Este archivo es el responsable de crear y configurar la conexión a la base de
datos para toda la aplicación utilizando SQLAlchemy en modo asíncrono.

Componentes Clave:
1. `async_engine`: Una instancia única del motor de base de datos que gestiona
   las conexiones a bajo nivel. Se crea una sola vez cuando se inicia la app.
2. `async_session_factory`: Una "fábrica" que produce objetos de sesión de
   SQLAlchemy (`AsyncSession`). Cada vez que se necesita interactuar con la
   base de datos (ej: dentro de un manejador de comandos), se solicita una nueva
   sesión a esta fábrica.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import settings

# Se crea una única instancia del motor asíncrono para toda la aplicación.
# Este objeto gestiona un pool de conexiones a la base de datos.
async_engine = create_async_engine(
    settings.database_url,

    # `echo=True` mostraría todas las sentencias SQL que se ejecutan en la consola.
    # Es muy útil para depurar, pero debe estar en `False` en producción.
    echo=False,
)

# Se crea una fábrica de sesiones. Esta fábrica se usará en toda la aplicación
# para obtener una nueva sesión de corta duración cada vez que se necesite
# realizar una operación en la base de datos.
async_session_factory = async_sessionmaker(
    bind=async_engine,

    # `expire_on_commit=False` es crucial en aplicaciones asíncronas.
    # Evita que SQLAlchemy invalide los objetos (ej: un 'Character') después de un
    # `session.commit()`. Sin esto, acceder a un atributo de un objeto después
    # de un commit podría lanzar un error al intentar recargarlo desde una
    # sesión ya cerrada.
    expire_on_commit=False
)