# Runegram MUD

![Python](https://img.shields.io/badge/python-3.11-blue.svg)![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)![Redis](https://img.shields.io/badge/redis-%23DD0_031.svg?style=for-the-badge&logo=redis&logoColor=white)

Runegram es un proyecto para crear un juego de rol textual multijugador (MUD - Multi-User Dungeon) que se juega a través de la interacción con un bot de Telegram. Este repositorio contiene una base funcional para una aplicación escalable, con registro de jugadores, un mundo explorable y herramientas de administración.

## Arquitectura y Stack Tecnológico

La arquitectura está diseñada para ser robusta, modular y escalable, utilizando tecnologías modernas:

*   **Lenguaje**: Python 3.11 con `asyncio`.
*   **Framework de Bot**: Aiogram.
*   **Contenerización**: Docker & Docker Compose.
*   **Base de Datos**: PostgreSQL para la persistencia de datos.
*   **Almacenamiento en Memoria**: Redis para gestión de estados de conversación (FSM).
*   **ORM**: SQLAlchemy (Asíncrono) para la interacción con la base de datos.
*   **Migraciones de BD**: Alembic para gestionar la evolución del esquema de la base de datos de forma segura.

## Funcionalidades Implementadas

*   **Entorno Automatizado:** Un script (`entrypoint.sh`) asegura que las migraciones de la base de datos se apliquen automáticamente al iniciar el bot, garantizando consistencia.
*   **Flujo de Jugador Completo:** Registro de cuentas, creación de personajes y persistencia de estado.
*   **Mundo de Juego Dinámico:**
    *   Sistema de salas (`Rooms`) conectadas por salidas (`Exits`) bidireccionales.
    *   Las salidas son entidades propias en la base de datos, preparadas para tener propiedades individuales como `locks`.
    *   Movimiento de jugadores entre salas mediante comandos de texto (ej: `norte`).
    *   Presentación de salas con formato de MUD clásico, mostrando nombre, descripción, objetos y salidas.
*   **Sistema de Objetos (Items):**
    *   Los objetos pueden existir en el mundo (en el suelo de una sala) o en el inventario de un personaje.
    *   Bucle de interacción completo: `/mirar` muestra los objetos, `/coger` los mueve al inventario, `/inventario` los muestra, y `/dejar` los devuelve a la sala.
*   **Herramientas de Administración:**
    *   Sistema de roles (`JUGADOR`, `ADMINISTRADOR`) para control de permisos.
    *   Comandos protegidos para crear y modificar el mundo en tiempo real: `/crearsala`, `/describirsala`, `/conectarsala`, `/teleport`, `/crearitem`.
*   **Arquitectura de Comandos Unificada y Escalable:**
    *   **Todos los comandos (jugador y admin) usan el prefijo `/`**, proporcionando una interfaz de usuario consistente.
    *   El sistema se basa en **clases `Command`** agrupadas en **`Command Sets`** (ej: `general`, `interaction`, `building`).
    *   Un **dispatcher central** procesa todos los comandos, verifica permisos y delega la ejecución a la clase correspondiente, haciendo que añadir nuevos comandos sea trivial.

## Estructura del Proyecto (Arquitectura Refactorizada)

La estructura actual está altamente organizada y desacoplada.

```
runegram/
├── alembic/              # Migraciones de la base de datos
├── commands/             # Clases de Comandos (la lógica de cada acción)
│   ├── admin/
│   └── player/
├── scripts/              # Scripts de utilidad (ej: full_reset.bat)
├── src/                  # Código fuente principal de la aplicación
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
├── requirements.txt      # Dependencias de Python
└── run.py                # Punto de entrada para iniciar la aplicación
```

## Puesta en Marcha

Se necesita Docker y Docker Compose.

1.  **Configurar el Entorno:** Crea un archivo `.env` en la raíz del proyecto a partir del ejemplo de abajo y añade tu token de bot de Telegram.
2.  **Ejecutar el Script de Reinicio:** Para asegurar un entorno limpio, usa el script automatizado.
    ```bash
    # En Windows (CMD o PowerShell)
    scripts\full_reset.bat
    ```
    Este script reconstruirá la imagen, levantará los servicios y aplicará todas las migraciones de la base de datos.
3.  **Jugar:** Abre Telegram y envía `/start` a tu bot.

---

## Visión a Futuro y Tareas Pendientes (TODO)

Esta sección documenta las próximas mejoras para evolucionar de un esqueleto funcional a un juego completo.

### 🚀 **Próximas Grandes Funcionalidades**

*   #### Terminar el Sistema de Locks y Permisos
    *   **Visión:** Crear un sistema de permisos granular para controlar el acceso a salidas, objetos y comandos.
    *   **Tareas:**
        1.  **Expandir el Parser de Locks:** Mejorar `permission_service` para que entienda una sintaxis más rica: `tiene_objeto(llave_oxidada)`, `habilidad(forzar_cerraduras)>25`, `clase(guerrero)`. Implementar operadores lógicos `y` / `o`.
        2.  **Crear Comandos de Admin:** Añadir `/lock [salida/objeto] con [string_de_lock]` y `/unlock [salida/objeto]` para que los constructores puedan asegurar partes del mundo.
        3.  **Integrar en el Juego:** Aplicar la verificación de `locks` en el dispatcher de movimiento y en el método `execute` de comandos como `/coger`.

*   #### Sistema de Interacción Detallada (`mirar`)
    *   **Visión:** Permitir al jugador examinar en detalle cualquier entidad del juego (objetos, otros jugadores, NPCs, elementos de la sala).
    *   **Tareas:**
        1.  **Refactorizar `CmdLook`:** El comando `/mirar [objetivo]` debe ser capaz de identificar el `objetivo` (un objeto en el suelo, un objeto en el inventario, otro jugador en la sala).
        2.  **Descripciones Detalladas:** Añadir un campo `look_description` a los modelos `Item`, `Character` y `NPC` que se mostrará al examinarlos.
        3.  **Palabras Clave en la Sala:** Implementar un sistema para que la descripción de una sala pueda tener `palabras clave` que, al ser "miradas", revelen información adicional.

*   #### Definir y Construir el Sistema de Combate y Habilidades
    *   **Visión:** Crear un sistema de combate y progresión de habilidades basado en una mecánica de d100 (tirada de 100 caras).
    *   **Tareas:**
        1.  **Modelos de Datos:** Crear los modelos `Skill` y `CharacterSkill` para almacenar las habilidades y el progreso de cada personaje. Añadir atributos de combate (Salud, Maná, Energía) al modelo `Character`.
        2.  **Mecánica d100:** Implementar la lógica central de "aprender haciendo": una acción tiene éxito si `d100 <= nivel_de_habilidad`, y al tener éxito, se gana experiencia.
        3.  **Comandos de Combate:** Crear el `CommandSet` de combate con comandos básicos como `/atacar [objetivo]`.
        4.  **Crear NPCs (Monstruos):** Diseñar un modelo `NPC` con atributos de combate y un comportamiento básico (IA simple).

### ✨ **Sugerencias Adicionales para el Futuro**

*   **Sistema de Clases y Razas:** Permitir a los jugadores elegir una clase (Guerrero, Mago) y raza (Humano, Elfo) durante la creación de personaje, lo que afectaría a sus habilidades y atributos iniciales.
*   **Gestión de `CommandSets` Dinámica:** Implementar la lógica para que el `dispatcher` lea los `command_sets` del personaje desde la base de datos, y añadir/quitar sets basados en el equipo o la sala.
*   **Sistema de Crafteo:** Crear objetos a partir de materiales. Requeriría `CommandSets` especiales cerca de estaciones de trabajo (forja, mesa de alquimia).
*   **Broadcasting de Mensajes:** Mejorar el comando `/decir` para que los mensajes sean vistos por todos los jugadores en la misma sala, creando una verdadera interacción social.
*   **Persistencia de NPCs y "Respawns":** Crear un sistema para que los monstruos y NPCs reaparezcan después de un tiempo de ser derrotados o de que el servidor se reinicie.
