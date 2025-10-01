# Runegram MUD

![Python](https://img.shields.io/badge/python-3.11-blue.svg)![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

**Runegram** es un motor de juego de rol textual multijugador (MUD - Multi-User Dungeon) diseñado para ser jugado a través de la interacción con un bot de Telegram. Este repositorio contiene el código fuente de un motor de juego funcional, construido con una arquitectura moderna, escalable y centrada en la separación entre la lógica del motor y el contenido del juego.

Este documento es una guía de inicio rápido. Para una documentación exhaustiva sobre la arquitectura, los sistemas del motor y las guías de creación de contenido, por favor, consulta la **[Documentación Completa](./docs/)**.

---

## Puesta en Marcha Rápida

Este proyecto está completamente contenerizado con Docker, por lo que no necesitas instalar Python o PostgreSQL en tu máquina.

**Requisitos:**
*   [Docker](https://www.docker.com/products/docker-desktop/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

**Pasos:**

1.  **Clona el Repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/runegram.git
    cd runegram
    ```

2.  **Configura el Entorno:**
    Crea un archivo `.env` en la raíz del proyecto. Puedes copiar el archivo de ejemplo (`.env.example` si lo tienes) y rellenar las variables, especialmente `BOT_TOKEN` y `SUPERADMIN_TELEGRAM_ID`.

3.  **Ejecuta el Script de Reinicio:**
    Para asegurar un entorno limpio, usa el script automatizado. Este script construirá la imagen Docker, creará los contenedores y volúmenes, y aplicará todas las migraciones de la base de datos.
    ```bash
    # En Windows (CMD o PowerShell)
    scripts\full_reset.bat
    ```

4.  **¡A Jugar!**
    Una vez que los contenedores estén en marcha, abre Telegram y envía `/start` a tu bot.

---

## Documentación Detallada

Toda la documentación exhaustiva sobre la arquitectura, los sistemas del motor, las guías para crear contenido y la visión a futuro del proyecto se encuentra en la carpeta `docs/`.

### Índice de Documentación

#### **Introducción**
*   **[01 - Guía de Inicio para Desarrolladores](./docs/01_GETTING_STARTED.md)**: Pasos detallados para configurar el entorno de desarrollo.
*   **[02 - Filosofía del Núcleo](./docs/02_CORE_PHILOSOPHY.md)**: Explicación en profundidad de los principios de diseño del motor.

#### **Sistemas del Motor**
*   **[03.1 - Sistema de Comandos](./docs/03_ENGINE_SYSTEMS/01_COMMAND_SYSTEM.md)**: Cómo funciona el dispatcher, los CommandSets y la generación dinámica de comandos.
*   **[03.2 - Sistema de Permisos (Locks)](./docs/03_ENGINE_SYSTEMS/02_PERMISSION_SYSTEM.md)**: Documentación del motor de `locks` basado en `ast`.
*   **[03.3 - Sistema de Prototipos](./docs/03_ENGINE_SYSTEMS/03_PROTOTYPE_SYSTEM.md)**: El sistema "Data-Driven" para `Items` y `Rooms`.
*   **[03.4 - Motor de Scripts](./docs/03_ENGINE_SYSTEMS/04_SCRIPTING_ENGINE.md)**: El sistema dual de Eventos y Tickers.
*   **[03.5 - Sistemas Sociales](./docs/03_ENGINE_SYSTEMS/05_SOCIAL_SYSTEMS.md)**: Documentación de Canales y Presencia (online/AFK).

#### **Creación de Contenido**
*   **[04.1 - Creando Comandos](./docs/04_CONTENT_CREATION/01_CREATING_COMMANDS.md)**: Guía práctica para añadir nuevos comandos al juego.
*   **[04.2 - Construyendo el Mundo](./docs/04_CONTENT_CREATION/02_BUILDING_THE_WORLD.md)**: Tutorial para añadir nuevas salas, objetos y canales.
*   **[04.3 - Escribiendo Scripts](./docs/04_CONTENT_CREATION/03_WRITING_SCRIPTS.md)**: Guía para usar `on_look`, `tickers` y crear nuevas funciones de script.

#### **Guías Adicionales**
*   **[05 - Guía de Administración](./docs/05_ADMIN_GUIDE.md)**: Manual de uso para todos los comandos de administración.
*   **[06 - Base de Datos y Migraciones](./docs/06_DATABASE_AND_MIGRATIONS.md)**: El flujo de trabajo con `Alembic`.
*   **[07 - Visión a Futuro (Roadmap)](./docs/07_ROADMAP.md)**: Las próximas grandes funcionalidades y mejoras.