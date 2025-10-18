---
título: "Sistema de Prototipos"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-18"
autor: "Proyecto Runegram"
etiquetas: ["prototipos", "dirigido-por-datos", "motor-contenido", "objetos", "salas", "fixtures", "world-loader"]
documentos_relacionados:
  - "creacion-de-contenido/construccion-de-salas.md"
  - "creacion-de-contenido/creacion-de-items.md"
  - "creacion-de-contenido/objetos-de-ambiente.md"
  - "arquitectura/overview.md"
referencias_código:
  - "game_data/item_prototypes.py"
  - "game_data/room_prototypes.py"
  - "src/models/item.py"
  - "src/models/room.py"
  - "src/services/world_loader_service.py"
estado: "actual"
---

# Prototype System

El Sistema de Prototipos es la implementación central de la filosofía "Motor vs. Contenido" en Runegram. Es un enfoque de diseño dirigido por datos (Data-Driven) que separa la **definición** de una entidad de su **instancia** en el mundo.

## 1. El Concepto: Prototipo vs. Instancia

Para entender el sistema, es crucial diferenciar estos dos conceptos:

*   **Prototipo (El "Plano"):**
    *   **¿Qué es?** Es la plantilla o el plano maestro que define un *tipo* de entidad. Contiene todos los datos base que son comunes a todas las entidades de ese tipo.
    *   **¿Dónde vive?** En los archivos de `game_data/` (ej: `item_prototypes.py`, `room_prototypes.py`).
    *   **Ejemplo:** El prototipo de la "espada viviente" define que su nombre es "una espada viviente", su descripción, que susurra cada 2 minutos, y que brilla al ser mirada.

*   **Instancia (La "Copia"):**
    *   **¿Qué es?** Es una copia única y específica de un prototipo que existe en el mundo del juego en un momento dado.
    *   **¿Dónde vive?** Como una fila en una tabla de la base de datos (ej: la tabla `items` o `rooms`).
    *   **Ejemplo:** Pueden existir tres "espadas vivientes" en el juego. Cada una es una `Instancia` diferente (con un `id` único en la tabla `items`), pero todas apuntan al mismo `Prototipo` "espada_viviente" a través de su columna `key`.

## 2. Ventajas del Sistema de Prototipos

Este enfoque ofrece enormes ventajas en escalabilidad y mantenimiento:

1.  **Eficiencia de Datos:** La base de datos no necesita almacenar el nombre, la descripción, los scripts y los tickers de cada una de las 100 espadas del juego. Solo almacena la `key` del prototipo y su ubicación. El resto de la información se lee desde el diccionario de prototipos en memoria.
2.  **Facilidad de Creación de Contenido:** Para crear un nuevo tipo de objeto, un diseñador solo necesita añadir una nueva entrada al diccionario `ITEM_PROTOTYPES`. No se requiere ninguna modificación en el código del motor ni en el esquema de la base de datos.
3.  **Actualizaciones Globales Sencillas:** Si necesitas corregir un error en la descripción de la "espada viviente", solo lo cambias en el prototipo. Automáticamente, todas las instancias de esa espada en el juego reflejarán el cambio.

## 3. Estructura de los Prototipos

### Prototipos de Objetos (`item_prototypes.py`)

La clave del diccionario es una `key` única para el tipo de objeto.

```python
"cofre_roble": {
    # --- Atributos Básicos ---
    "name": "un cofre de roble",
    "keywords": ["cofre", "roble"],
    "description": "Un pesado cofre de madera con refuerzos de hierro.",

    # --- Atributos de Comportamiento (Opcional) ---
    "scripts": { "on_look": "script_notificar_brillo_magico(color=tenue)" },
    "tick_scripts": [{ "interval_ticks": 60, "script": "...", "permanent": True }],

    # --- Atributos de Sistema (Opcional) ---
    "grants_command_sets": ["secretos_cofre"],
    "locks": "rol(SUPERADMIN) or tiene_objeto(llave_maestra)",

    # --- Atributos de Contenedor (Opcional) ---
    "is_container": True,
    "capacity": 20,

    # --- Atributos de Fixture (Opcional) ---
    "is_fixture": False  # Si es True, el objeto es un fixture (objeto de ambiente)
}
```
*   **`locks`**: Para un objeto normal, restringe el comando `/coger`. Para un contenedor, restringe `/meter`, `/sacar` y `/inv`.
*   **`is_container`**: Si es `True`, el objeto puede contener otros ítems.
*   **`capacity`**: El número máximo de ítems que puede albergar el contenedor.
*   **`is_fixture`**: Si es `True`, el objeto es un fixture (objeto de ambiente fijo en una sala).

### Prototipos de Salas (`room_prototypes.py`)

La clave del diccionario es una `key` única para la sala, utilizada para las conexiones.

```python
"plaza_central": {
    # --- Atributos Básicos ---
    "name": "Plaza Central de Runegard",
    "description": "Estás en el corazón de la ciudad...",

    # --- Atributos de Conexión (Opcional) ---
    "exits": {
        "norte": {
            "to": "puerta_del_norte",
            "locks": "tiene_objeto(salvoconducto_real)"
        },
        "este": "calle_mercaderes" # Sintaxis simple
    },

    # --- Atributos de Sistema (Opcional) ---
    "grants_command_sets": ["comercio_ciudad"],

    # --- Atributos de Entorno (Opcional) ---
    "fixtures": [
        "fuente_magica_plaza",
        "arbol_frutal_plaza"
    ],
    "details": {
        "bandera": {
            "keywords": ["bandera", "estandarte"],
            "description": "Una bandera azul con el escudo del reino..."
        }
    }
}
```
*   **`exits`**: Puede usar una sintaxis simple (`"direccion": "destino"`) para una salida bidireccional sin `lock`, o una sintaxis avanzada (`"direccion": {"to": "destino", "locks": "..."}`) para añadir un `lock` a la salida de ida.
*   **`fixtures`**: Lista de claves de items que forman parte permanente del ambiente. Se sincronizan automáticamente al iniciar el bot.
*   **`details`**: Permite definir elementos de la descripción que se pueden `mirar` con `/mirar [keyword]` sin ser objetos físicos.

## 4. Conexión en el Código (Modelos)

Los modelos de SQLAlchemy (`Item` y `Room`) actúan como el puente entre la **Instancia** (base de datos) y el **Prototipo** (código) a través de una propiedad `@property`.

```python
# En src/models/item.py

class Item(Base):
    # ... columnas de la instancia (id, key, room_id) ...

    @property
    def prototype(self) -> dict:
        """
        Esta propiedad busca en el diccionario ITEM_PROTOTYPES usando
        la `self.key` de la instancia y devuelve el diccionario del prototipo.
        """
        return ITEM_PROTOTYPES.get(self.key, {})
```

Todos los servicios y comandos del motor interactúan con las instancias de los modelos, pero utilizan la propiedad `.prototype` para acceder a la definición de contenido, manteniendo la separación limpia.

## 5. Sincronización de Fixtures (World Loader)

Los fixtures son objetos de ambiente definidos en el campo `fixtures` de los prototipos de sala. El `world_loader_service` los sincroniza automáticamente al iniciar el bot en el **PASO 4** de `sync_world_from_prototypes()`.

### Proceso de Sincronización

1. **Lectura de Prototipos**: Lee el campo `fixtures` de cada sala en `ROOM_PROTOTYPES`
2. **Verificación de Existencia**: Para cada fixture, verifica si ya existe en la sala
3. **Creación o Mantenimiento**:
   - Si NO existe: crea nuevo fixture
   - Si YA existe: lo mantiene (preserva `script_state`)
4. **Registro**: Loguea todas las operaciones realizadas

### Características Clave

**Idempotente**: Reiniciar el bot múltiples veces no duplicará fixtures.

**Preserva Estado**: El campo `script_state` (estado persistente) se mantiene en reinicios.

**Seguro**: Solo crea nuevos fixtures, nunca elimina existentes.

### Ejemplo de Código

```python
# En src/services/world_loader_service.py

async def _sync_room_fixtures(session: AsyncSession, room_key_to_id_map: dict):
    """
    Sincroniza los fixtures (objetos de ambiente) definidos en las salas.
    Esta función es idempotente: no duplicará fixtures en reinicios.
    """
    for room_key, room_data in ROOM_PROTOTYPES.items():
        fixture_keys = room_data.get("fixtures", [])

        for item_key in fixture_keys:
            # Verificar si el fixture ya existe
            existing_fixture = await session.execute(
                select(Item).where(Item.key == item_key, Item.room_id == room_id)
            )

            if not existing_fixture:
                # Crear nuevo fixture
                new_fixture = Item(key=item_key, room_id=room_id)
                session.add(new_fixture)
```

**Ver**: [Objetos de Ambiente](../creacion-de-contenido/objetos-de-ambiente.md) para documentación completa sobre fixtures.

## Ver También

- [Building Rooms](../creacion-de-contenido/construccion-de-salas.md) - Cómo crear prototipos de salas
- [Creating Items](../creacion-de-contenido/creacion-de-items.md) - Cómo crear prototipos de items
- [Objetos de Ambiente](../creacion-de-contenido/objetos-de-ambiente.md) - Guía completa de fixtures
- [Scripting System](sistema-de-scripts.md) - Agregar comportamiento a prototipos
