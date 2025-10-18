---
título: "Guía de Instalación"
categoría: "Comenzando"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["instalación", "configuración", "docker", "comenzando"]
documentos_relacionados:
  - "filosofia-central.md"
  - "../arquitectura/configuracion.md"
  - "../arquitectura/migraciones-de-base-de-datos.md"
referencias_código:
  - "docker-compose.yml"
  - "scripts/full_reset.bat"
  - "alembic/"
estado: "actual"
---

# Guía de Inicio para Desarrolladores

Este documento proporciona una guía detallada paso a paso para configurar el entorno de desarrollo de Runegram en una máquina local. El proyecto está completamente contenerizado con Docker, lo que simplifica enormemente el proceso de instalación.

## 1. Prerrequisitos

Antes de comenzar, asegúrate de tener instalado el siguiente software:

*   **[Git](https://git-scm.com/)**: Para clonar el repositorio.
*   **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**: Gestiona los contenedores, imágenes y volúmenes. Incluye `docker` y `docker-compose`.

## 2. Proceso de Instalación

### Paso 1: Clonar el Repositorio

Abre tu terminal preferida, navega al directorio donde quieres guardar el proyecto y clona el repositorio desde GitHub.

```bash
git clone https://github.com/tu-usuario/runegram.git
cd runegram
```

### Paso 2: Configurar las Variables de Entorno

La aplicación utiliza un archivo `.env` en la raíz del proyecto para gestionar secretos y configuraciones específicas del entorno. Este archivo **no se debe subir a Git**.

1.  Crea un nuevo archivo llamado `.env` en la raíz del proyecto.
2.  Copia y pega el siguiente contenido en el archivo:

    ```env
    # ===============================================================
    #          Archivo de Configuración de Entorno para Runegram
    # ===============================================================

    # --- Configuración del Superadministrador ---
    # El ID numérico de Telegram del usuario que tendrá el rol más alto.
    # Puedes obtener tu ID hablando con bots como @userinfobot en Telegram.
    SUPERADMIN_TELEGRAM_ID=123456789

    # --- Telegram ---
    # El token de autenticación para tu bot de Telegram, proporcionado por @BotFather.
    BOT_TOKEN=TU_TOKEN_DE_BOTFATHER_AQUI

    # --- Base de Datos (PostgreSQL) ---
    # Credenciales para el servicio de la base de datos.
    POSTGRES_USER=runegram
    POSTGRES_PASSWORD=runegram
    POSTGRES_DB=runegram_db
    POSTGRES_HOST=postgres
    POSTGRES_PORT=5432

    # --- Caché y Estados (Redis) ---
    # Configuración para la conexión al servicio de Redis.
    REDIS_HOST=redis
    REDIS_PORT=6379
    REDIS_DB=0
    ```

3.  **Modifica las variables `SUPERADMIN_TELEGRAM_ID` y `BOT_TOKEN` con tus propios valores.**

### Paso 3: Construir y Ejecutar los Contenedores

El proyecto incluye un script de conveniencia que automatiza todo el proceso de limpieza y arranque.

Desde la raíz del proyecto, ejecuta:
```bash
# En Windows (CMD o PowerShell)
scripts\full_reset.bat
```
Este script realizará las siguientes acciones:
1.  `docker-compose down -v`: Detiene y elimina los contenedores existentes y, crucialmente, **borra el volumen de la base de datos**, asegurando un estado completamente limpio.
2.  `docker-compose up --build -d`: Reconstruye la imagen de la aplicación (si hay cambios en el `Dockerfile` o `requirements.txt`) y levanta todos los servicios (`bot`, `postgres`, `redis`) en segundo plano.

### Paso 4: Verificar la Instalación

Tras ejecutar el script, puedes verificar que todo está funcionando correctamente:

1.  **Comprueba los contenedores en ejecución:**
    ```bash
    docker ps
    ```
    Deberías ver tres contenedores en estado `Up`: `runegram-bot-1`, `runegram-postgres-1` y `runegram-redis-1`.

2.  **Revisa los logs de la aplicación:**
    ```bash
    docker-compose logs -f bot
    ```
    Espera a que el proceso de arranque finalice. Verás los logs del `entrypoint.sh` esperando a PostgreSQL, ejecutando las migraciones y, finalmente, el bot de Python iniciándose. La última línea debería ser similar a:
    `[INFO] - aiogram.dispatcher.dispatcher: Start polling.`

### Paso 5: ¡A Jugar!
Abre tu cliente de Telegram, busca tu bot y envíale el comando `/start`. ¡Deberías recibir el mensaje de bienvenida!

## 3. Flujo de Trabajo de Desarrollo

### Realizar Cambios en el Código
Gracias a los volúmenes de Docker configurados en `docker-compose.yml`, cualquier cambio que hagas en los archivos de tu máquina local (en `src/`, `commands/`, `game_data/`, etc.) se refleja **instantáneamente** dentro del contenedor. El servidor de Aiogram se reiniciará automáticamente para aplicar la mayoría de los cambios en el código Python.

### Gestionar Migraciones de la Base de Datos
Cuando modificas la estructura de un modelo en `src/models/` (ej: añades una nueva columna), debes generar y aplicar una migración.

1.  **Generar una nueva migración:**
    ```bash
    docker-compose exec bot alembic revision --autogenerate -m "Un mensaje descriptivo del cambio"
    ```
2.  **Revisar el archivo generado:** Es una buena práctica abrir el nuevo archivo en `alembic/versions/` para asegurarte de que los cambios generados son los que esperabas.
3.  **Aplicar la migración:** La forma más segura de aplicar la nueva migración en un entorno de desarrollo es reiniciar todo el sistema.
    ```bash
    scripts\full_reset.bat
    ```

### Comandos Útiles de Docker
*   `docker-compose up -d`: Levanta los servicios en segundo plano.
*   `docker-compose down`: Detiene y elimina los contenedores.
*   `docker-compose logs -f bot`: Muestra los logs del contenedor del bot en tiempo real.
*   `docker-compose exec bot <comando>`: Ejecuta un comando dentro del contenedor del bot (ej: `docker-compose exec bot alembic current`).

---

## Próximos Pasos

- Lee [Core Philosophy](filosofia-central.md) para entender los principios de diseño
- Consulta [Configuration System](../arquitectura/configuracion.md) para personalizar el comportamiento
- Explora [Database and Migrations](../arquitectura/migraciones-de-base-de-datos.md) para entender el modelo de datos

---

**Changelog:**
- **2025-10-09**: Migrado a nueva estructura con YAML frontmatter
- **2025-01-09**: Versión original
