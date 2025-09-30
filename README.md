# Runegram MUD

![Python](https://img.shields.io/badge/python-3.11-blue.svg)![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

Runegram es un proyecto para crear un juego de rol textual multijugador (MUD - Multi-User Dungeon) que se juega a través de la interacción con un bot de Telegram. Este repositorio contiene el motor de un juego funcional, con una arquitectura escalable lista para la expansión masiva de contenido.

## Filosofía de Diseño: Motor vs. Contenido

La arquitectura del proyecto se divide en dos conceptos clave para máxima escalabilidad y facilidad de mantenimiento:

1.  **El Motor del Juego (`src/`):** Contiene el **código fuente** de la aplicación. Es la maquinaria genérica que hace que el juego funcione (conexión a la base de datos, comunicación con Telegram, ejecución de lógica). No sabe qué es una "espada", solo sabe cómo manejar un "Ítem".
2.  **El Contenido del Juego (`game_data/`, `commands/`):** Contiene los **datos y definiciones** que dan vida al mundo. Aquí se define qué es una "espada", qué hace el comando "atacar", o qué monstruos existen. Está diseñado para que los diseñadores de juego puedan añadir contenido sin tocar el motor principal.

## Sistemas Clave Implementados

### 1. Carga del Mundo Dirigida por Datos
El mundo estático del juego ya no se construye con comandos de administrador, sino que se define enteramente en archivos de datos.

*   **Definición (`game_data/room_prototypes.py`):** Todas las salas, sus descripciones y las conexiones entre ellas se definen en un diccionario de Python. Esto actúa como el "mapa maestro" del mundo.
*   **Sincronización (`world_loader_service.py`):** Al iniciar el bot, un servicio dedicado lee estos prototipos, comprueba el estado de la base de datos y crea o actualiza las salas y salidas para que coincidan con la "fuente de la verdad". Esto garantiza un mundo consistente en cada reinicio.

### 2. Sistema de Comandos Dinámicos y Contextuales
La lista de comandos disponibles para un jugador no es estática; cambia en tiempo real según su contexto.

*   **Múltiples Fuentes:** Un `command_service` centralizado construye la lista de `CommandSets` activos para un jugador a partir de:
    1.  **Base:** Comandos innatos del personaje, guardados en la base de datos.
    2.  **Equipo:** Objetos en el inventario que otorgan `CommandSets` (ej: unas ganzúas que otorgan el set `thievery`).
    3.  **Entorno:** La sala actual, que puede otorgar `CommandSets` (ej: una forja que otorga el set `smithing`).
    4.  **Rol:** Los administradores reciben sets de comandos especiales.
*   **Actualización en Telegram:** El motor actualiza la lista de comandos (`/`) en el cliente de Telegram del jugador en tiempo real, cada vez que su contexto cambia (al moverse de sala, coger un objeto, etc.), proporcionando una experiencia de usuario fluida e intuitiva.

### 3. Sistema Dual de Scripts: Eventos y Tickers
El motor permite que el contenido del juego ejecute lógica a través de dos sistemas complementarios.

*   **Scripts Reactivos (Eventos):** Son disparados por acciones del jugador.
    *   **Trigger:** `"on_look": "script_nombre(...)"` en el prototipo de un objeto.
    *   **Ejecución:** Cuando un jugador mira el objeto, el `script_service` ejecuta la función correspondiente.
*   **Scripts Proactivos (Tickers):** Se ejecutan de forma programada, independientemente de la acción del jugador, haciendo que el mundo se sienta vivo.
    *   **Definición:** `"tickers": [{"schedule": "*/5 * * * *", "script": "...", "category": "ambient"}]`
    *   **Ejecución:** Un `ticker_service` (usando `APScheduler`) se encarga de ejecutar estos scripts según su horario (cron o intervalo).
    *   **Inteligencia:** Los tickers de categoría `"ambient"` solo se ejecutan para jugadores considerados "activos", evitando notificar a usuarios que no están jugando.

### 4. Sistema de Canales y Presencia
Para facilitar la comunicación y la inmersión social, el juego implementa un sistema de canales y seguimiento de actividad.

*   **Seguimiento de Actividad (`online_service.py`):** Utilizando **Redis** para máxima velocidad, el motor registra un timestamp cada vez que un jugador envía un comando. Si la última actividad fue hace menos de 5 minutos, se le considera "online".
*   **Canales (`channel_service.py`):**
    *   Se definen en `game_data/channel_prototypes.py`.
    *   Los jugadores pueden suscribirse o desuscribirse (`/canal activar/desactivar`).
    *   Permiten comunicación global (ej: `/novato [mensaje]`) entre todos los jugadores suscritos.
    *   El comando `/quien` utiliza el `online_service` para mostrar una lista de los jugadores activos.

## Estructura del Proyecto

```
runegram/
├── alembic/              # Migraciones de la base de datos
├── commands/             # DEFINICIÓN de los comandos (clases Command)
│   ├── admin/
│   └── player/
├── game_data/            # DEFINICIÓN del contenido del juego
│   ├── channel_prototypes.py # Define los canales de chat
│   ├── item_prototypes.py    # Define los prototipos de objetos
│   └── room_prototypes.py    # Define el mapa del mundo (salas y salidas)
├── scripts/              # Scripts de utilidad (ej: full_reset.bat)
├── src/                  # CÓDIGO FUENTE del motor de la aplicación
│   ├── bot/
│   ├── handlers/
│   │   └── player/
│   │       └── dispatcher.py # El router de comandos principal
│   ├── models/           # Modelos de datos de SQLAlchemy
│   ├── services/         # Lógica de negocio y acceso a datos
│   │   ├── broadcaster_service.py
│   │   ├── channel_service.py
│   │   ├── command_service.py
│   │   ├── online_service.py
│   │   ├── script_service.py
│   │   ├── ticker_service.py
│   │   └── world_loader_service.py
│   └── utils/
├── .env                  # Archivo de variables de entorno (ignorado)
├── docker-compose.yml    # Orquestación de los contenedores
├── Dockerfile            # Definición de la imagen Docker de la app
├── entrypoint.sh         # Script de arranque
└── run.py                # Punto de entrada
```

## Puesta en Marcha

Se necesita Docker y Docker Compose.

1.  **Configurar el Entorno:** Crea un archivo `.env` en la raíz del proyecto a partir del `.env.example`.
2.  **Ejecutar el Script de Reinicio:** Para asegurar un entorno limpio, usa el script automatizado.
    ```bash
    # En Windows
    scripts\full_reset.bat
    ```
    Este script reconstruirá la imagen, levantará los servicios y aplicará todas las migraciones.
3.  **Jugar:** Abre Telegram y envía `/start` a tu bot.

---

## Visión a Futuro y Tareas Pendientes (TODO)

Esta sección documenta las próximas mejoras para evolucionar de un motor robusto a un juego completo y pulido.

### 🚀 **Próximas Grandes Funcionalidades**

*   #### **Sistema de Combate y Habilidades**
    *   **Visión:** Crear un sistema de combate y progresión de habilidades basado en una mecánica de d100 (tirada de 100 caras).
    *   **Tareas:**
        1.  **Modelos de Datos:** Crear los modelos `Skill` y `CharacterSkill`. Añadir atributos de combate (Salud, Maná, etc.) al modelo `Character`.
        2.  **Mecánica d100:** Implementar la lógica de "aprender haciendo": una acción tiene éxito si `d100 <= nivel_de_habilidad`, y al tener éxito, se gana experiencia.
        3.  **PNJs y Spawners:** Crear `npc_prototypes.py`, un modelo `NPC` y un `npc_service` para poder "spawnear" monstruos en el mundo y gestionar su IA (agresiva, pasiva) y sus "respawns".
        4.  **Comandos de Combate:** Crear el `CommandSet` de combate (`/atacar`, `/huir`, etc.).

*   #### **Completar el Sistema de Locks y Permisos**
    *   **Visión:** Crear un sistema de permisos granular para controlar el acceso a salidas, objetos y comandos, yendo más allá del simple `rol()`.
    *   **Tareas:**
        1.  **Expandir el Parser:** Mejorar `permission_service` para que entienda una sintaxis rica: `tiene_objeto(llave_oxidada)`, `habilidad(forzar_cerraduras)>25`, `clase(guerrero)`. Implementar operadores lógicos `y` / `o`.
        2.  **Integración:** Aplicar la verificación de `locks` en el `CmdMove` para las salidas y en el `dispatcher` para los comandos.

### ✨ **Mejoras del Motor y Calidad de Vida**

*   **Bandeja de Entrada para Notificaciones:** Para los tickers de categoría `important` o `quest`, guardar los mensajes para los jugadores inactivos y presentárselos cuando vuelvan a conectarse ("Mientras no estabas...").
*   **Sistema de Contenedores:** Expandir los ítems para que puedan ser contenedores (mochilas, cofres) con su propio inventario, capacidad y `locks`.
*   **Sistema de Clases y Razas:** Usar una **Máquina de Estados Finitos (FSM)** para guiar al jugador a través de una creación de personaje por pasos, permitiéndole elegir clase y raza, lo que a su vez establecerá sus `CommandSets` base en la BD.
*   **Mejorar Comando `/decir`:** Hacer que el comando `/decir` y las acciones de combate envíen mensajes a todos los jugadores *online* en la misma sala, creando una verdadera interacción social.

### 🌍 **Contenido y Expansión del Mundo**

*Gracias a la arquitectura Data-Driven, expandir el mundo es ahora una tarea de diseño, no de programación.*
*   **Crear Nuevos Prototipos:** Diseñar más objetos, monstruos y PNJ en los archivos de `game_data`.
*   **Diseñar Zonas:** Expandir el `room_prototypes.py` para crear nuevas áreas, ciudades y mazmorras.
*   **Escribir Quests:** Implementar PNJ que puedan dar misiones, utilizando el sistema de `FSM` para rastrear el progreso del jugador en una quest.
*   **Crear Habilidades y Clases:** Definir las habilidades disponibles en el juego y los `CommandSets` que cada clase aprenderá a medida que progrese.