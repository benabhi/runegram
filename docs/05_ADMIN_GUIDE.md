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
*   **Descripción:** Crea una instancia del objeto especificado por su `clave_prototipo` y la coloca en el suelo de la sala actual del administrador. La clave debe corresponder a una entrada en `game_data/item_prototypes.py`.
*   **Uso:**
    ```
    /generarobjeto espada_viviente
    ```

---

## Comandos de Movimiento

Estos comandos permiten a los administradores moverse libremente por el mundo.

### `/teleport <id_sala>`
*   **Alias:** `/tp`
*   **Permiso:** `ADMIN`
*   **Descripción:** Te teletransporta instantáneamente a la sala especificada por su `ID` numérico. Para encontrar el ID de una sala, utiliza el comando `/listarsalas`.
*   **Uso:**
    ```
    /tp 3
    ```

---

## Comandos de Información y Diagnóstico

Estos comandos son herramientas de solo lectura para inspeccionar el estado del juego.

### `/listarsalas [category:X] [tag:Y]`
*   **Alias:** `/lsalas`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra una lista de todas las salas que existen en el mundo, incluyendo su `ID`, su `key` de prototipo y su `nombre`. Soporta filtrado por categoría y tags. Esencial para usar `/teleport`.
*   **Uso:**
    ```
    /listarsalas                        # Todas las salas
    /listarsalas category:ciudad_runegard  # Solo salas de esa categoría
    /listarsalas tag:exterior           # Solo salas con ese tag
    ```

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

### `/listaritems [category:X] [tag:Y]`
*   **Alias:** `/litems`
*   **Permiso:** `ADMIN`
*   **Descripción:** Lista items filtrados por categoría y tags. Muestra ubicación (inventario/sala/contenedor), categoría y tags de cada item.
*   **Uso:**
    ```
    /listaritems                    # Todos los items
    /listaritems category:arma      # Solo items de esa categoría
    /listaritems tag:magica         # Solo items con ese tag
    ```
*   **Notas:** Límite de 20 resultados.

### `/categorias`
*   **Alias:** `/cats`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra todas las categorías disponibles de salas e items.
*   **Notas:** Útil para conocer qué categorías están definidas en los prototipos antes de filtrar.

### `/tags`
*   **Alias:** `/etiquetas`
*   **Permiso:** `ADMIN`
*   **Descripción:** Muestra todos los tags disponibles de salas e items.
*   **Notas:** Útil para conocer qué tags están definidos en los prototipos antes de filtrar.

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