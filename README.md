# Runegram MUD

![Python](https://img.shields.io/badge/python-3.11-blue.svg)![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

Runegram es un proyecto para crear un juego de rol textual multijugador (MUD - Multi-User Dungeon) que se juega a través de la interacción con un bot de Telegram. Este repositorio contiene el motor de un juego funcional, con una arquitectura escalable lista para la expansión masiva de contenido.

## Filosofía de Diseño: Motor vs. Contenido

La arquitectura del proyecto se divide en dos conceptos clave para máxima escalabilidad y facilidad de mantenimiento:

1.  **El Motor del Juego (`src/`):** Contiene el **código fuente** de la aplicación. Es la maquinaria genérica que hace que el juego funcione (conexión a la base de datos, comunicación con Telegram, ejecución de lógica). No sabe qué es una "espada", solo sabe cómo manejar un "Ítem".
2.  **El Contenido del Juego (`game_data/`, `commands/`):** Contiene los **datos y definiciones** que dan vida al mundo. Aquí se define qué es una "espada", qué hace el comando "atacar", o qué monstruos existen. Está diseñado para que los diseñadores de juego puedan añadir contenido sin tocar el motor principal.

## Sistemas Clave Implementados

### 1. Sistema de Comandos Unificado
Todos los comandos (de jugador y de administrador) están implementados como clases que heredan de una `Command` base.
*   **Command Sets:** Los comandos se agrupan en `Command Sets` (ej: `general`, `interaction`, `building`), que son listas de instancias de comandos.
*   **Dispatcher Central:** Un único handler en `src/handlers/player/dispatcher.py` intercepta todos los mensajes, determina qué `Command Sets` están activos para el jugador, busca el comando correspondiente y lo ejecuta. Esto hace que añadir nuevos comandos sea tan simple como crear una nueva clase y añadirla a una lista.

### 2. Sistema de Prototipos
Para separar los datos del código, las entidades del juego como los objetos se definen usando un sistema de prototipos.
*   **Definición (`game_data/`):** Se crea una "plantilla" para cada tipo de objeto en un diccionario de Python (ej: `ITEM_PROTOTYPES`). Esta plantilla contiene todos los datos base: nombre, descripción, `keywords` para búsqueda, y scripts de eventos.
*   **Instancia (Base de Datos):** La base de datos no almacena todos estos datos. La tabla `items` solo guarda una "instancia" ligera que apunta a la `key` del prototipo (ej: `espada_corta`) y cualquier dato que sea único para esa copia específica (como `name_override`).
*   **Ventaja:** Para crear 100 tipos de espadas, solo necesitas añadir 100 entradas al diccionario de prototipos, sin modificar la base de datos ni la lógica del motor.

### 3. Sistema de Eventos (Scripts)
El motor está preparado para que el contenido del juego pueda ejecutar lógica del motor a través de un sistema de scripts.
*   **Disparadores (Triggers):** Los prototipos pueden definir scripts para eventos específicos (ej: `"on_look": "script_nombre(...)"`).
*   **Script Service:** Un servicio central (`script_service.py`) mantiene un registro de todas las funciones de script disponibles.
*   **Ejecución:** Cuando un evento ocurre en el juego (ej: un jugador mira un objeto), el motor busca si el prototipo del objeto tiene un script para ese evento. Si lo tiene, llama al `Script Service` para que ejecute la función de lógica correspondiente.
*   **Implementado:** `on_look` para ítems.

## Estructura del Proyecto

```
runegram/
├── alembic/              # Migraciones de la base de datos
├── commands/             # DEFINICIÓN de los comandos (clases Command)
│   ├── admin/
│   └── player/
├── game_data/            # DEFINICIÓN de prototipos (items, NPCs, etc.)
├── scripts/              # Scripts de utilidad (ej: full_reset.bat)
├── src/                  # CÓDIGO FUENTE del motor de la aplicación
│   ├── bot/              # Configuración del bot y dispatcher central de Aiogram
│   ├── config.py         # Carga de variables de entorno
│   ├── db.py             # Configuración del motor de SQLAlchemy
│   ├── handlers/         # Punto de entrada de Telegram a la app
│   │   └── player/
│   │       └── dispatcher.py # El dispatcher/router de comandos principal
│   ├── models/           # Modelos de datos de SQLAlchemy
│   ├── services/         # Lógica de negocio y acceso a datos
│   └── utils/            # Funciones de ayuda (ej: presenters)
├── .env                  # Archivo de variables de entorno (ignorado)
├── docker-compose.yml    # Orquestación de los contenedores
├── Dockerfile            # Definición de la imagen Docker de la app
├── entrypoint.sh         # Script de arranque que ejecuta migraciones
└── run.py                # Punto de entrada para iniciar la aplicación
```

## Puesta en Marcha

Se necesita Docker y Docker Compose.

1.  **Configurar el Entorno:** Crea un archivo `.env` en la raíz del proyecto.
2.  **Ejecutar el Script de Reinicio:** Para asegurar un entorno limpio, usa el script automatizado.
    ```bash
    # En Windows (CMD o PowerShell)
    scripts\full_reset.bat
    ```
    Este script reconstruirá la imagen, levantará los servicios y aplicará todas las migraciones.
3.  **Jugar:** Abre Telegram y envía `/start` a tu bot.

---

## Visión a Futuro y Tareas Pendientes (TODO)

Esta sección documenta las próximas mejoras para evolucionar de un esqueleto funcional a un juego completo.

### 🚀 **Próximas Grandes Funcionalidades**

*   #### Terminar el Sistema de Locks y Permisos
    *   **Visión:** Crear un sistema de permisos granular para controlar el acceso a salidas, objetos y comandos.
    *   **Tareas:**
        1.  **Expandir el Parser de Locks:** Mejorar `permission_service` para que entienda una sintaxis más rica: `tiene_objeto(llave_oxidada)`, `habilidad(forzar_cerraduras)>25`, `clase(guerrero)`. Implementar operadores lógicos `y` / `o`.
        2.  **Crear Comandos de Admin:** Añadir `/lock [salida] con [string_de_lock]` y `/unlock [salida]` para que los constructores puedan asegurar partes del mundo.
        3.  **Integrar en el Juego:** Aplicar la verificación de `locks` en el dispatcher de movimiento.

*   #### Sistema de Interacción Detallada (`mirar`)
    *   **Visión:** Permitir al jugador examinar en detalle cualquier entidad del juego (objetos, otros jugadores, NPCs, elementos de la sala).
    *   **Tareas:**
        1.  **Refactorizar `CmdLook`:** El comando `/mirar [objetivo]` ya busca objetos. Se debe expandir para que pueda identificar a otros jugadores y NPCs en la sala.
        2.  **Palabras Clave en la Sala:** Implementar un sistema para que la descripción de una sala pueda tener `keywords` que, al ser "miradas", revelen información adicional sin ser objetos físicos.

*   #### Definir y Construir el Sistema de Combate y Habilidades
    *   **Visión:** Crear un sistema de combate y progresión de habilidades basado en una mecánica de d100 (tirada de 100 caras).
    *   **Tareas:**
        1.  **Modelos de Datos:** Crear los modelos `Skill` y `CharacterSkill`. Añadir atributos de combate (Salud, Maná, etc.) al modelo `Character`.
        2.  **Mecánica d100:** Implementar la lógica central de "aprender haciendo": una acción tiene éxito si `d100 <= nivel_de_habilidad`, y al tener éxito, se gana experiencia.
        3.  **Comandos de Combate:** Crear el `CommandSet` de combate con comandos básicos como `/atacar [objetivo]`.
        4.  **Crear Prototipos de NPCs:** Añadir un archivo `npc_prototypes.py` en `game_data` y un modelo `NPC` para poder "spawnear" monstruos en el mundo.

### ✨ **Sugerencias Adicionales para el Futuro**

*   **Gestión de `CommandSets` Dinámica:** Implementar la lógica para que el `dispatcher` lea los `command_sets` del personaje desde la base de datos, y añadir/quitar sets basados en el equipo o la sala.
*   **Broadcasting de Mensajes:** Mejorar el comando `/decir` y las acciones de combate para que los mensajes sean vistos por todos los jugadores en la misma sala, creando una verdadera interacción social.
*   **Sistema de Clases y Razas:** Usar el sistema de **FSM (Máquina de Estados Finitos)** para guiar al jugador a través de una creación de personaje por pasos, permitiéndole elegir clase y raza.
*   **Persistencia de NPCs y "Respawns":** Crear un sistema para que los monstruos y NPCs reaparezcan después de un tiempo de ser derrotados.
*   **Sistema de Contenedores:** Expandir los ítems para que puedan ser contenedores (ej: una mochila, un cofre) con su propio inventario y `locks`.
