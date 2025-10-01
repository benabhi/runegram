# Sistema de Prototipos

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

1.  **Eficiencia de Datos:** La base de datos no necesita almacenar el nombre, la descripción, los scripts y los tickers de cada una de las 100 espadas del juego. Solo almacena la `key` del prototipo y su ubicación. El resto de la información se lee desde el diccionario de prototipos en memoria, que es mucho más rápido.
2.  **Facilidad de Creación de Contenido:** Para crear un nuevo tipo de objeto, un diseñador solo necesita añadir una nueva entrada al diccionario `ITEM_PROTOTYPES`. No se requiere ninguna modificación en el código del motor ni en el esquema de la base de datos.
3.  **Actualizaciones Globales Sencillas:** Si necesitas corregir un error de tipeo en la descripción de la "espada viviente", solo lo cambias en un lugar: el prototipo. Automáticamente, todas las instancias de esa espada en el juego reflejarán el cambio la próxima vez que sean examinadas.

## 3. Estructura de los Prototipos

### Prototipos de Objetos (`item_prototypes.py`)

La clave del diccionario es una `key` única para el tipo de objeto.

```python
"espada_viviente": {
    # (Obligatorio) El nombre que ven los jugadores.
    "name": "una espada viviente",

    # (Obligatorio) Palabras clave para interactuar (ej: /mirar espada).
    "keywords": ["espada", "viviente"],

    # (Obligatorio) Descripción mostrada con /mirar.
    "description": "La hoja de acero parece retorcerse...",

    # (Opcional) Scripts reactivos a eventos del jugador.
    "scripts": {
        "on_look": "script_notificar_brillo_magico(color=rojo)"
    },

    # (Opcional) Scripts proactivos que se ejecutan periódicamente.
    "tickers": [{
        "schedule": "*/2 * * * *",
        "script": "script_espada_susurra_secreto",
        "category": "ambient"
    }],

    # (Opcional) CommandSets que este objeto otorga a su portador.
    "grants_command_sets": ["magia_oscura"],

    # (Opcional) Restricciones para interactuar con el objeto.
    "locks": "rol(ADMIN)"
}
```

### Prototipos de Salas (`room_prototypes.py`)

La clave del diccionario es una `key` única para la sala, utilizada para las conexiones.

```python
"plaza_central": {
    # (Obligatorio) El nombre de la sala.
    "name": "Plaza Central de Runegard",

    # (Obligatorio) La descripción principal de la sala.
    "description": "Estás en el corazón de la ciudad...",

    # (Opcional) Conexiones a otras salas.
    "exits": {
        "norte": "puerta_del_norte",
        "este": "calle_mercaderes"
    },

    # (Opcional) CommandSets que esta sala otorga a quienes estén en ella.
    "grants_command_sets": ["comercio_ciudad"]
}
```

## 4. Conexión en el Código (Modelos)

Los modelos de SQLAlchemy (`Item` y `Room`) actúan como el puente entre la **Instancia** (base de datos) y el **Prototipo** (código).

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