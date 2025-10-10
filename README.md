# Runegram MUD

![Python](https://img.shields.io/badge/python-3.11-blue.svg)![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

**Runegram** es un motor de juego de rol textual multijugador (MUD - Multi-User Dungeon) diseñado para ser jugado a través de la interacción con un bot de Telegram. Este repositorio contiene el código fuente de un motor de juego funcional, construido con una arquitectura moderna, escalable y centrada en la separación entre la lógica del motor y el contenido del juego.

Este documento es una guía de inicio rápido. Para una documentación exhaustiva sobre la arquitectura, los sistemas del motor y las guías de creación de contenido, por favor, consulta la **[Documentación Completa](./docs/)**.

---

## Filosofía de Diseño

### Motor vs. Contenido
La arquitectura del proyecto se divide en dos conceptos clave para máxima escalabilidad y facilidad de mantenimiento:

1.  **El Motor del Juego (`src/`):** Contiene el **código fuente** en **inglés**. Es la maquinaria genérica que hace que el juego funcione. No sabe qué es una "espada", solo sabe cómo manejar un `Item`.
2.  **El Contenido del Juego (`game_data/`, `commands/`):** Contiene los **datos y definiciones** en **español** (o el idioma del juego). Aquí se define qué es una "espada", qué hace el comando `/atacar`, etc.

### Filosofía de Comandos
Los comandos en Runegram buscan ser simples, descriptivos e intuitivos. Se prefiere la claridad de tener más comandos dedicados (ej: `/activarcanal`, `/desactivarcanal`) a la complejidad de un único comando con múltiples subcomandos. El formato preferido es `/<acción> [argumentos]`.

Además, el motor del juego genera dinámicamente comandos de comunicación a partir del contenido definido en `game_data`. Si un diseñador crea un nuevo canal de chat llamado "Comercio" (`comercio`), el comando `/comercio [mensaje]` estará disponible automáticamente para los jugadores.

---

## Puesta en Marcha Rápida

**Requisitos:**
*   [Docker](https://www.docker.com/products/docker-desktop/) y Docker Compose.

**Pasos:**

1.  **Clona el Repositorio** y entra en el directorio.
2.  **Configura el Entorno:** Crea un archivo `.env` en la raíz del proyecto y rellena las variables, especialmente `BOT_TOKEN` y `SUPERADMIN_TELEGRAM_ID`.
3.  **Ejecuta el Script de Reinicio:**
    ```bash
    # En Windows (CMD o PowerShell)
    scripts\full_reset.bat
    ```
4.  **¡A Jugar!** Abre Telegram y envía `/start` a tu bot.

---

## Configuración

Runegram utiliza un **sistema de configuración híbrido** que separa:

- **`.env`** - Credenciales sensibles (tokens, passwords) - **NO subir a Git**
- **`gameconfig.toml`** - Configuración del juego (tiempos, límites, comportamiento) - **SÍ en Git**

### Archivos de Configuración

#### `.env` (Credenciales)
Contiene tokens y passwords que nunca deben subirse a Git:
```bash
BOT_TOKEN=tu_token_de_telegram
SUPERADMIN_TELEGRAM_ID=tu_telegram_id
POSTGRES_PASSWORD=runegram
# ... más credenciales
```

#### `gameconfig.toml` (Configuración del Juego)
Contiene configuración modificable del comportamiento del juego:
```toml
[online]
threshold_minutes = 5  # Tiempo de inactividad antes de marcar offline

[pulse]
interval_seconds = 2  # Intervalo del pulse global

[pagination]
items_per_page = 30  # Items por página en listados
```

**Ver:** [Documentación Completa de Configuración](./docs/architecture/configuration.md)

---

## Características Principales

### Sistemas del Motor Implementados

- **🏗️ Sistema de Comandos Dinámicos** - Los comandos disponibles cambian según el contexto del personaje (ubicación, equipo, rol)
- **📡 Sistema de Broadcasting** - Mensajes a salas y canales globales de comunicación
- **⏰ Sistema de Pulse Global** - Corazón temporal del juego que sincroniza todos los sistemas basados en tiempo (ticks cada 2s)
- **📜 Sistema de Scripts** - Ejecuta código Python en respuesta a eventos del juego
- **🗂️ Sistema de Prototipos** - Define contenido reutilizable (salas, items) separado del motor
- **🏷️ Sistema de Categories y Tags** - Organiza y busca contenido eficientemente usando categorías únicas y etiquetas múltiples (inspirado en Evennia)
- **💬 Sistema de Canales** - Canales estáticos de comunicación global + canales dinámicos creados por jugadores
- **🎨 Sistema de Templates** - Separación de presentación y lógica usando Jinja2
- **🔘 Sistema de Botones Inline** - Interacción mejorada con botones de Telegram
- **👥 Sistema de Online/AFK** - Detección de jugadores activos vs. desconectados con notificaciones sociales

**Ver:** [Sistemas del Motor Completos](./docs/engine-systems/) para detalles de implementación.

---

## Documentación Detallada

Toda la documentación exhaustiva sobre la arquitectura, los sistemas del motor, las guías para crear contenido y la visión a futuro del proyecto se encuentra en la carpeta `docs/`.

**Índice de Documentación:**
- **[📚 Documentación Principal](./docs/README.md)** - Índice maestro de toda la documentación
- **[🚀 Guía de Inicio](./docs/getting-started/installation.md)** - Primeros pasos para desarrolladores
- **[📖 Referencia de Comandos](./docs/reference/command-reference.md)** - Lista completa de comandos con ejemplos
- **[👨‍💼 Guía de Administración](./docs/admin-guide/admin-commands.md)** - Comandos y herramientas para administradores
- **[⚙️ Sistemas del Motor](./docs/engine-systems/README.md)** - Documentación técnica de sistemas internos
- **[🎨 Creación de Contenido](./docs/content-creation/README.md)** - Guías para diseñadores y builders

**[➡️ Acceder a la Documentación Completa](./docs/README.md)**