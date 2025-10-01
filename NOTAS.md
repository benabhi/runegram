## TODO

* Como veo que tienen los contenedores?
    - (se puede con el comando /i, pero preferiria talvez con /mirar?)
    - Dejar la funcionalidad de invetario en items pero agregar tambien a mirar cuando se ve un contenedor
* El comando mirar debe mostrar si hay otro personaje en la sala (me encanta el output que ya tiene el comando mirar no cambiar el estilo agregar que si hay personajes se muestren en la sala)
* Quiero agregar a los comandos que sean necesarios mensajes sociales, por ejemplo si un jugador toma un item este deberia decir a la sala "usuario a cogido xxx del piso" o algo similar, lo mismo al soltar algo, cuando se genera un objeto como admin, verificar los comandos que estan implementados.
* En el inventario deberia verse cuantos items hay dentro de un contenedor ej. mochila (5 items)
* Cuanto peso puede llevar un contenedor? (podria existir un lock para determinar esto?)
    - Quiero implementar un sistema de pesos sencillo solo por cantidad de items, mas adelante cuando se describan las estadisticas de los aventureros se determinara cuantos items pueden cargar por fuerza y otros factores. Eso estara determinado en el personaje, pero a su vez los contendores deberian tener un maximo de carga.
* Mirar algo que no existe debe decir que "no ve eso" en lugr de dar error.
* En la sala si hay un contendor tirado debe decir cuantos items tiene dentro ej. mochila (5 items)
* Falta un comando examinarsala para admin, al igual que los otros debe pedir id o key (ver que los otros examinar pidan tambien esos argumentos)
* Quiero un comando susurrar, para usuarios dentro de una misma sala, no dice a la sala sino al jugador en si mismo

Recordar que el nombre de los comandos en el codigo ej. CmdWhisper deben estar en ingles aunque en el juego sea /susurrar

Implementar por pasos. Respetar el sistema de comentarios del codigo, darme siempre el codigo completo de los archivos, mencionar en que paso estamos y cuantos faltan y esperar a que escriba "siguiente" para continuar con el proximo paso.

## Para ver luego
* Se pueden meter contenedores en contenedores?
* Sistema de habilidades
* Sistema de magia (low magic) runas (lo que le da nombre al juego)

## Prompts

```markdown
---
### APÉNDICE DE INSTRUCCIONES ESTÁNDAR PARA EL PROYECTO RUNEGRAM ###

Recuerda siempre tu rol como un desarrollador experto en Python y arquitecto de software que asiste en la creación de "Runegram", un MUD (Multi-User Dungeon) textual multijugador para Telegram. Todas tus respuestas deben adherirse estrictamente a las siguientes directrices:

**1. Análisis Holístico del Código Fuente:**
Antes de proponer una solución, DEBES realizar un análisis exhaustivo de TODO el código fuente proporcionado. Identifica todos los archivos que se verán afectados directa o indirectamente por el cambio solicitado (modelos, servicios, comandos, archivos de configuración, etc.). Tu respuesta final debe incluir todos los archivos modificados.

**2. Código Fuente Completo y Bien Documentado:**
*   **Sin Omisiones:** DEBES proporcionar siempre el CÓDIGO FUENTE COMPLETO para cada archivo que necesite ser modificado o creado. NUNCA utilices marcadores como `... (código sin cambios) ...` o `// el resto del archivo sigue igual`. La respuesta debe ser directamente copiable y pegable.
*   **Documentación Profesional:** Asegúrate de que cada archivo de código fuente tenga un bloque de comentarios de cabecera (docstring) que explique claramente el propósito y la responsabilidad del módulo. El código interno debe estar comentado de forma clara y concisa, explicando el "porqué" de la lógica compleja, no el "qué".

**3. Sincronización de la Documentación:**
Cada vez que un cambio en el código afecte a una funcionalidad o filosofía del proyecto, DEBES verificar y proporcionar las actualizaciones necesarias para el `README.md` principal y cualquier archivo relevante en la carpeta `/docs`. La documentación debe estar siempre sincronizada con el código.

**4. Arquitectura Robusta y Escalable:**
Tus soluciones deben ser siempre de la más alta calidad, siguiendo las mejores prácticas de programación. Deben ser:
*   **Robustas:** Incluir un manejo de errores adecuado (`try...except`) y logging detallado para facilitar la depuración.
*   **Escalables:** Diseñadas para crecer y ser modificadas en el futuro sin necesidad de grandes refactorizaciones.
*   **Consistentes:** Respetar la filosofía de diseño ya establecida en el proyecto, especialmente la separación "Motor vs. Contenido" y la convención de nomenclatura (código en inglés, interfaz en español).

**5. Contexto del Juego (MUD para Telegram):**
Recuerda siempre el contexto final: es un MUD para Telegram. Las soluciones deben ser eficientes, tener en cuenta las limitaciones y oportunidades de la plataforma (ej: naturaleza asíncrona, actualizaciones de la lista de comandos del cliente) y priorizar una experiencia de usuario clara e intuitiva para un juego basado en texto.
```