# Guía de Comandos de Administración

Este documento es una referencia completa para todos los comandos especiales disponibles para los roles de `ADMIN` y `SUPERADMIN`. Estos comandos son herramientas para la creación, depuración y gestión del mundo de Runegram.

## Jerarquía de Roles

El sistema de permisos se basa en una jerarquía simple:
*   **SUPERADMIN:** Tiene acceso a todos los comandos. Es el rol más alto.
*   **ADMIN:** Tiene acceso a la mayoría de los comandos de construcción y moderación, pero no a los que son potencialmente destructivos o alteran la configuración fundamental del juego.
*   **JUGADOR:** El rol base sin acceso a comandos administrativos.

---

## Comandos de Generación (Spawning)

Estos comandos permiten crear nuevas instancias de entidades en el mundo.

### `/generarobjeto <clave_prototipo>`
*   **Alias:** `/genobj`
*   **Permiso:** `ADMIN`
*   **Descripción:** Crea una instancia del objeto especificado por su `clave_prototipo` y la coloca en el suelo de la sala actual del administrador. La clave debe corresponder a una entrada en `game_data/item_prototypes.py`. Los jugadores online en la sala ven un mensaje narrativo evocativo y aleatorio sobre la aparición del objeto.
*   **Uso:**
    ```
    /generarobjeto espada_viviente
    ```
*   **Nota:** El mensaje de aparición varía aleatoriamente (ver [Sistema de Narrativa](./03_ENGINE_SYSTEMS/09_NARRATIVE_SERVICE.md)).

### `/destruirobjeto <id>`
*   **Alias:** `/delobj`
*   **Permiso:** `ADMIN`
*   **Descripción:** Elimina permanentemente una instancia de objeto del juego usando su ID numérico. El comportamiento de notificación depende de la ubicación del objeto:
    - **En sala:** Los jugadores online en la sala ven un mensaje narrativo evocativo sobre la desaparición
    - **En inventario:** El dueño recibe un mensaje privado + los jugadores en su sala ven un mensaje narrativo
    - **En contenedor:** Solo el admin recibe confirmación (sin notificación social)
*   **Uso:**
    ```
    /destruirobjeto 15
    ```
*   **Advertencia:** Esta acción es irreversible. Usa `/examinarobjeto <id>` antes para confirmar qué estás eliminando.
*   **Nota:** Los mensajes de destrucción varían aleatoriamente (ver [Sistema de Narrativa](./03_ENGINE_SYSTEMS/09_NARRATIVE_SERVICE.md)).

---

## Comandos de Movimiento

Estos comandos permiten a los administradores moverse libremente por el mundo.

### `/teleport <id_sala>`
*   **Alias:** `/tp`
*   **Permiso:** `ADMIN`
*   **Descripción:** Te teletransporta instantáneamente a la sala especificada por su `ID` numérico. Para encontrar el ID de una sala, utiliza el comando `/listarsalas`. Los jugadores online en la sala de origen ven un mensaje narrativo evocativo sobre tu salida, y los jugadores en la sala de destino ven un mensaje sobre tu llegada.
*   **Uso:**
    ```
    /tp 3
    ```
*   **Nota:** Los mensajes de teletransporte varían aleatoriamente (ver [Sistema de Narrativa](./03_ENGINE_SYSTEMS/09_NARRATIVE_SERVICE.md)).

---

## Comandos de Información y Diagnóstico

Estos comandos son herramientas de solo lectura para inspeccionar el estado del juego.

### `/listarsalas [cat:X] [tag:Y,Z]`
*   **Alias:** `/lsalas`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra una lista de todas las salas que existen en el mundo, incluyendo su `ID`, su `key` de prototipo y su `nombre`. Soporta filtrado por categoría y tags. Esencial para usar `/teleport`.
*   **Uso:**
    ```
    /listarsalas                        # Todas las salas
    /listarsalas cat:ciudad_runegard    # Solo salas de esa categoría
    /listarsalas tag:exterior           # Solo salas con ese tag
    /listarsalas tag:exterior,seguro    # Solo salas con ambos tags (AND)
    ```
*   **Sintaxis de filtros:**
    - `cat:X` - Filtra por categoría X
    - `tag:Y,Z` - Filtra por tags Y y Z (separados por coma, lógica AND)
*   **Notas:** Formato lista optimizado para móvil.

### `/examinarsala <id_o_key>`
*   **Alias:** `/exsala`
*   **Permiso:** `ADMIN`
*   **Descripción:** Examina información detallada de una sala por ID numérico o key de prototipo. Muestra ID, key, nombre, descripción, locks, salidas, objetos y personajes presentes.
*   **Uso:**
    ```
    /exsala 1
    /exsala plaza_central
    ```

### `/examinarpersonaje <nombre_o_id>`
*   **Alias:** `/exchar`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra un informe detallado sobre un personaje. Incluye su ID, sala actual, rol de cuenta, CommandSets base y contenido del inventario.
*   **Uso:**
    ```
    /exchar Ben
    /exchar 1
    ```

### `/examinarobjeto <id>`
*   **Alias:** `/exobj`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra un informe detallado sobre una **instancia** específica de un objeto, identificado por su ID único en la base de datos. Incluye su clave de prototipo, ubicación (sala o inventario de un jugador) y cualquier `override` de nombre o descripción.
*   **Uso:**
    ```
    /exobj 12
    ```

### `/validar`
*   **Alias:** `/reportevalidacion`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra un reporte de validación de integridad del sistema. Detecta conflictos de aliases entre comandos, keys duplicadas, y advertencias de configuración.
*   **Notas:** Útil para diagnosticar problemas después de modificar prototipos o comandos.

---

## Comandos de Búsqueda por Categories/Tags

Estos comandos permiten buscar y filtrar contenido del juego usando el sistema de categories y tags.

### `/listaritems [cat:X] [tag:Y,Z]`
*   **Alias:** `/litems`
*   **Permiso:** `ADMIN`
*   **Descripción:** Lista items filtrados por categoría y tags. Muestra ubicación (inventario/sala/contenedor), categoría y tags de cada item.
*   **Uso:**
    ```
    /listaritems                    # Todos los items
    /listaritems cat:arma           # Solo items de esa categoría
    /listaritems tag:magica         # Solo items con ese tag
    /listaritems tag:magica,unica   # Solo items con ambos tags (AND)
    ```
*   **Sintaxis de filtros:**
    - `cat:X` - Filtra por categoría X
    - `tag:Y,Z` - Filtra por tags Y y Z (separados por coma, lógica AND)
*   **Notas:** Límite de 20 resultados. Formato lista optimizado para móvil.

### `/listarcategorias`
*   **Alias:** `/cats`, `/lcats`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra todas las categorías disponibles de salas e items.
*   **Notas:** Útil para conocer qué categorías están definidas en los prototipos antes de filtrar. Formato lista optimizado para móvil.

### `/listartags`
*   **Alias:** `/etiquetas`, `/ltags`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra todos los tags disponibles de salas e items.
*   **Notas:** Útil para conocer qué tags están definidos en los prototipos antes de filtrar. Formato lista optimizado para móvil.

---

## Comandos de Gestión (Management)

Estos comandos modifican el estado fundamental de las entidades del juego y generalmente requieren el permiso más alto.

### `/asignarrol <nombre_personaje> <rol>`
*   **Permiso:** `SUPERADMIN`
*   **Descripción:** Cambia el rol de la cuenta asociada al personaje especificado. El Superadmin no puede asignar un rol igual o superior al suyo a otra persona.
*   **Roles Disponibles:** `JUGADOR`, `ADMIN`, `SUPERADMIN`.
*   **Uso:**
    ```
    /asignarrol Pippin ADMIN
    ```