# Filosofía del Núcleo de Runegram

La arquitectura de Runegram no es accidental; se basa en un conjunto de principios de diseño bien definidos. Comprender esta filosofía es clave para desarrollar y expandir el juego de manera consistente, mantenible y escalable.

Estos principios se dividen en dos áreas principales: la separación estructural entre el **Motor y el Contenido**, y el diseño de la interfaz de usuario a través de la **Filosofía de Comandos**.

## 1. El Principio del Motor vs. el Contenido (Data-Driven Design)

Este es el principio más fundamental de Runegram. El proyecto entero está dividido en dos dominios lógicos estrictamente separados:

### El Motor del Juego (`src/`)

*   **¿Qué es?** El Motor es el **código fuente** de la aplicación. Es la maquinaria genérica, abstracta y reutilizable que hace que el juego funcione.
*   **Responsabilidades:** Conexión a la base de datos, comunicación con Telegram, ejecución de la lógica de los sistemas (comandos, permisos, tickers), gestión de modelos de datos, etc.
*   **Cómo piensa:** El Motor no sabe qué es una "espada mágica" o la "Ciudad de Runegard". Solo conoce conceptos genéricos como `Item` y `Room`. No contiene nombres, descripciones ni reglas de juego específicas. Su trabajo es proporcionar un conjunto de herramientas potentes para que el Contenido pueda existir.

### El Contenido del Juego (`game_data/`, `commands/`)

*   **¿Qué es?** El Contenido son los **datos y definiciones** que dan vida, forma y reglas al mundo del juego.
*   **Responsabilidades:** Definir qué objetos existen (`item_prototypes.py`), cómo se conectan las salas (`room_prototypes.py`), qué canales de chat hay (`channel_prototypes.py`), qué hacen los comandos (`commands/`) y cómo reacciona el mundo (`scripts`).
*   **Cómo piensa:** El Contenido define qué es una "Espada Viviente", qué descripción tiene, qué hace cuando la miras y que susurra secretos cada dos minutos. Utiliza las herramientas que el Motor le proporciona para implementar estas reglas.

### La Ventaja de la Separación

Esta estricta separación (conocida como **diseño dirigido por datos** o *Data-Driven Design*) es la clave de la escalabilidad de Runegram:

1.  **Aceleración del Desarrollo:** Un diseñador de contenido puede crear cientos de salas, objetos y PNJ sin escribir una sola línea de código Python del motor. El desarrollo del mundo se convierte en una tarea de edición de archivos de datos, no de programación.
2.  **Reducción de Bugs:** Al aislar la lógica compleja en el Motor, se reduce drásticamente la superficie de ataque para los errores. Un error de tipeo en la descripción de un objeto no puede romper el servidor.
3.  **Mantenibilidad:** El Motor se puede refactorizar y mejorar de forma independiente sin afectar al Contenido, y viceversa.
4.  **Control de Versiones Claro:** Los cambios en el mundo del juego son visibles directamente en el historial de `git` de la carpeta `game_data/`, lo que permite un seguimiento y una colaboración mucho más sencillos.

## 2. La Filosofía de Comandos

La interfaz a través de la cual los jugadores interactúan con el mundo sigue una filosofía centrada en la claridad y la facilidad de uso.

### Principio de Comando Descriptivo

Se prefiere la claridad de tener **más comandos dedicados y explícitos** a la complejidad de tener un único comando con múltiples subcomandos.

*   **Ejemplo Bueno:** `/activarcanal`, `/desactivarcanal`, `/listarsalas`. Cada comando hace una sola cosa y su nombre lo describe.
*   **Ejemplo a Evitar:** `/canal set novato on`, `/admin salas listar`. Este enfoque, aunque potente, es menos intuitivo y más difícil de descubrir para el jugador.

El formato estándar para todos los comandos es `/<acción> [argumentos]`.

### Principio de Descubrimiento Dinámico

El motor del juego está diseñado para que la interfaz se adapte al contexto del jugador, ayudándole a descubrir las acciones disponibles.

*   **Generación Dinámica:** Los comandos de chat (como `/novato` o `/sistema`) no están hardcodeados. Se generan automáticamente al leer los prototipos de canal. Si un diseñador añade un nuevo canal de chat `comercio`, el comando `/comercio` pasa a existir sin necesidad de programación adicional.
*   **Actualización en Vivo:** El motor actualiza la lista de comandos disponibles en el menú (`/`) del cliente de Telegram en tiempo real. Si un jugador coge un objeto que le otorga una nueva habilidad (y por tanto, un nuevo comando), ese comando aparecerá inmediatamente en su lista. Esto elimina la necesidad de que los jugadores memoricen comandos contextuales.

Estos principios combinados buscan crear una experiencia de juego fluida, donde la interfaz es una ayuda y no un obstáculo, y donde el mundo puede crecer y evolucionar de forma rápida y segura.