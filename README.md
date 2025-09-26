# Runegram MUD

![Python](https://img.shields.io/badge/python-3.11-blue.svg)![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

Runegram es un proyecto para crear un juego de rol textual multijugador (MUD - Multi-User Dungeon) que se juega a través de la interacción con un bot de Telegram. Este repositorio contiene la estructura base para una aplicación escalable y fácil de mantener, lista para que se empiece a construir la lógica del juego.

## Stack Tecnológico

La arquitectura del proyecto está diseñada para ser robusta y escalable, utilizando tecnologías modernas:

*   **Lenguaje**: Python 3.11
*   **Framework de Bot**: Aiogram
*   **Contenerización**: Docker & Docker Compose
*   **Base de Datos**: PostgreSQL
*   **Almacenamiento en Memoria**: Redis (para FSM - Máquina de Estados Finitos y caché)
*   **ORM**: SQLAlchemy
*   **Migraciones de BD**: Alembic

## Estructura del Proyecto

La estructura está organizada para separar responsabilidades y facilitar el crecimiento del proyecto.

```
runegram/
├── alembic/              # Migraciones de base de datos de Alembic
├── src/                  # Código fuente principal de la aplicación
│   ├── __init__.py
│   ├── bot/              # Configuración del bot y dispatcher de Aiogram
│   ├── config.py         # Carga de variables de entorno y configuración
│   ├── handlers/         # Manejadores de comandos y mensajes de Telegram
│   ├── models/           # Modelos de datos de SQLAlchemy
│   └── services/         # Lógica de negocio y servicios del juego
├── .env                  # Archivo local para variables de entorno (ignorado por Git)
├── .gitignore            # Archivos y directorios a ignorar por Git
├── alembic.ini           # Configuración de Alembic
├── docker-compose.yml    # Orquestación de los contenedores de Docker
├── Dockerfile            # Definición de la imagen Docker para la app Python
├── requirements.txt      # Dependencias de Python
└── run.py                # Punto de entrada para iniciar la aplicación
```

## Puesta en Marcha

Para levantar el proyecto, solo necesitas tener Docker y Docker Compose instalados.

### 1. Prerrequisitos

*   [Docker](https://www.docker.com/get-started)
*   [Docker Compose](https://docs.docker.com/compose/install/) (generalmente viene incluido con Docker Desktop)

### 2. Configuración del Entorno

El bot necesita algunas variables de entorno para funcionar, principalmente el token de Telegram.

1.  **Crear el archivo `.env`**:
    Copia el contenido de abajo y pégalo en un nuevo archivo llamado `.env` en la raíz del proyecto.

    ```env
    # Telegram Bot Token (obtenido de @BotFather)
    BOT_TOKEN=TU_BOT_TOKEN_AQUI

    # Configuración de PostgreSQL
    POSTGRES_USER=runegram
    POSTGRES_PASSWORD=supersecret
    POSTGRES_DB=runegram_db
    POSTGRES_HOST=postgres
    POSTGRES_PORT=5432

    # Configuración de Redis
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_DB=0
    ```

2.  **Añadir tu Token**:
    Reemplaza `TU_BOT_TOKEN_AQUI` con el token que te proporcionó `@BotFather` en Telegram.

### 3. Construir y Ejecutar con Docker

Abre una terminal en la raíz del proyecto y ejecuta el siguiente comando:

```bash
docker-compose up --build
```

Este comando hará lo siguiente:
*   Construirá la imagen de Docker para la aplicación de Python, instalando todas las dependencias.
*   Levantará los contenedores para el bot, la base de datos PostgreSQL y Redis.
*   Conectará todos los contenedores en una misma red para que puedan comunicarse.
*   Mostrará los logs de todos los servicios en tiempo real.

Para ejecutar los contenedores en segundo plano, puedes usar:
```bash
docker-compose up --build -d
```

### 4. Verificar que todo funciona

*   **Logs**: Deberías ver en la terminal un mensaje que dice `INFO:root:Bot iniciando...` seguido de `INFO:aiogram.dispatcher.dispatcher:Start polling.`.
*   **Telegram**: Abre Telegram, busca tu bot y envíale el comando `/start`. Debería responderte con: `¡Hola, mundo! Runegram está en línea.`

Para detener todos los servicios, presiona `Ctrl + C` en la terminal donde se están ejecutando, o ejecuta `docker-compose down` si los lanzaste en segundo plano.

---