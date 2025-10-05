# Plan: Sistema de Categories y Tags para Runegram

## 📋 Análisis y Justificación

### ✅ La idea ES EXCELENTE y tiene mucho sentido

**Razones:**

1. **Búsqueda y Filtrado Mejorados**
   - Actualmente NO hay forma de buscar "todas las salas del bosque oscuro"
   - NO se puede listar "todos los items tipo arma" fácilmente
   - Categories/Tags solucionan esto elegantemente

2. **Organización de Contenido**
   - A medida que el juego crece, necesitas agrupar:
     - Salas por zonas: bosques, ciudades, mazmorras, etc.
     - Items por tipos: armas, armaduras, consumibles, quest items
     - NPCs por facciones, roles, etc.

3. **Comandos de Admin Potentes**
   - `/listar rooms category:bosque_oscuro`
   - `/buscar items tag:arma tag:legendaria`
   - `/tp_category ciudad_principal` (tp a primera sala de esa categoría)

4. **Sistemas Futuros** que se benefician:
   - **Clima/Ambiente**: Aplicar efectos a todas las salas `category:exterior`
   - **Spawn de Mobs**: Generar enemigos en salas con `tag:mazmorra`
   - **Quests**: "Visita 5 salas con tag:bosque_oscuro"
   - **Scripts de Eventos**: Ejecutar en grupos de objetos
   - **Balanceo**: Encontrar rápidamente items con `tag:arma` para ajustar stats

5. **Compatible con Arquitectura Actual**
   - Los prototipos son diccionarios Python
   - Agregar `category` y `tags` es trivial
   - No rompe nada existente

### 🔍 Comparación con Evennia

Evennia usa exactamente este sistema:
- **Category (Categoría)**: `String` - Un objeto pertenece a UNA categoría
  - Ejemplos: `"zona_bosque"`, `"tipo_arma"`, `"faccion_guardia"`
- **Tags (Etiquetas)**: `List[str]` - Un objeto puede tener MÚLTIPLES tags
  - Ejemplos: `["oscuro", "peligroso", "exterior"]`, `["arma", "espada", "legendaria"]`

**Es el estándar de la industria MUD** y funciona muy bien.

---

## 🚀 Plan de Implementación

### Fase 1: Prototipos Únicamente (RECOMENDADO EMPEZAR AQUÍ)

**Ventajas:**
- ✅ Simple, sin cambios en BD ni migraciones
- ✅ Se define todo en el contenido (prototipos)
- ✅ Fácil de implementar y probar
- ✅ Cubre el 90% de casos de uso

**Desventajas:**
- ❌ No se pueden cambiar categories/tags dinámicamente en runtime
- ❌ Todos los objetos del mismo prototipo comparten category/tags

#### 1.1. Actualizar Estructura de Prototipos

**`game_data/room_prototypes.py`:**
```python
ROOM_PROTOTYPES = {
    "claro_bosque_1": {
        "name": "Claro del Bosque Oscuro",
        "description": "Un claro entre árboles antiguos y retorcidos.",
        "category": "el_bosque_oscuro",  # UNA categoría (opcional)
        "tags": ["bosque", "exterior", "peligroso"],  # MÚLTIPLES tags (opcional)
        "exits": {
            "norte": "claro_bosque_2",
            "sur": "entrada_bosque"
        }
    },

    "plaza_central": {
        "name": "Plaza Central de Runegard",
        "description": "El corazón de la ciudad...",
        "category": "ciudad_runegard",
        "tags": ["ciudad", "seguro", "social"],
        "exits": {...}
    }
}
```

**`game_data/item_prototypes.py`:**
```python
ITEM_PROTOTYPES = {
    "espada_herrumbrosa": {
        "name": "Espada Herrumbrosa",
        "description": "...",
        "category": "arma",  # Categoría de tipo de item
        "tags": ["espada", "una_mano", "metal"],  # Características específicas
        "stackable": False,
        "attributes": {
            "damage": 5
        }
    },

    "pocion_vida_menor": {
        "name": "Poción de Vida Menor",
        "description": "...",
        "category": "consumible",
        "tags": ["pocion", "curacion", "apilable"],
        "stackable": True,
        "attributes": {
            "heal_amount": 20
        }
    }
}
```

#### 1.2. Agregar Métodos de Acceso a Modelos

**`src/models/room.py`:**
```python
@property
def category(self) -> str | None:
    """Retorna la categoría de esta sala desde su prototipo."""
    return self.prototype.get("category")

@property
def tags(self) -> list[str]:
    """Retorna los tags de esta sala desde su prototipo."""
    return self.prototype.get("tags", [])
```

**`src/models/item.py`:**
```python
@property
def category(self) -> str | None:
    """Retorna la categoría de este item desde su prototipo."""
    return self.prototype.get("category")

@property
def tags(self) -> list[str]:
    """Retorna los tags de este item desde su prototipo."""
    return self.prototype.get("tags", [])
```

#### 1.3. Crear `tag_service.py`

**`src/services/tag_service.py`:**
```python
"""
Servicio para búsqueda y filtrado por Categories y Tags.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Room, Item

async def find_rooms_by_category(session: AsyncSession, category: str) -> list[Room]:
    """Encuentra todas las salas de una categoría."""
    result = await session.execute(select(Room))
    all_rooms = result.scalars().all()
    return [room for room in all_rooms if room.category == category]

async def find_rooms_by_tag(session: AsyncSession, tag: str) -> list[Room]:
    """Encuentra todas las salas con un tag específico."""
    result = await session.execute(select(Room))
    all_rooms = result.scalars().all()
    return [room for room in all_rooms if tag in room.tags]

async def find_rooms_by_tags_all(session: AsyncSession, tags: list[str]) -> list[Room]:
    """Encuentra salas que tienen TODOS los tags especificados."""
    result = await session.execute(select(Room))
    all_rooms = result.scalars().all()
    return [room for room in all_rooms if all(tag in room.tags for tag in tags)]

async def find_rooms_by_tags_any(session: AsyncSession, tags: list[str]) -> list[Room]:
    """Encuentra salas que tienen AL MENOS UNO de los tags."""
    result = await session.execute(select(Room))
    all_rooms = result.scalars().all()
    return [room for room in all_rooms if any(tag in room.tags for tag in tags)]

# Equivalentes para Items
async def find_items_by_category(session: AsyncSession, category: str) -> list[Item]:
    """Encuentra todos los items de una categoría."""
    result = await session.execute(select(Item))
    all_items = result.scalars().all()
    return [item for item in all_items if item.category == category]

async def find_items_by_tag(session: AsyncSession, tag: str) -> list[Item]:
    """Encuentra todos los items con un tag específico."""
    result = await session.execute(select(Item))
    all_items = result.scalars().all()
    return [item for item in all_items if tag in item.tags]

# Funciones de utilidad
def get_all_categories_from_rooms() -> set[str]:
    """Retorna todas las categorías únicas de salas desde prototipos."""
    from game_data.room_prototypes import ROOM_PROTOTYPES
    categories = set()
    for proto in ROOM_PROTOTYPES.values():
        if cat := proto.get("category"):
            categories.add(cat)
    return categories

def get_all_tags_from_rooms() -> set[str]:
    """Retorna todos los tags únicos de salas desde prototipos."""
    from game_data.room_prototypes import ROOM_PROTOTYPES
    tags = set()
    for proto in ROOM_PROTOTYPES.values():
        tags.update(proto.get("tags", []))
    return tags
```

#### 1.4. Comandos de Admin

**`commands/admin/search.py`** (nuevo archivo):
```python
class CmdListRooms(Command):
    """Lista salas filtradas por category o tags."""
    names = ["listar_rooms", "list_rooms"]
    lock = "role:ADMIN"
    description = "Lista salas. Uso: /listar_rooms [category:X] [tag:Y]"

    async def execute(self, character, session, message, args):
        from src.services import tag_service

        if not args:
            # Listar todas
            result = await session.execute(select(Room))
            rooms = result.scalars().all()
        else:
            # Parsear filtros
            category_filter = None
            tag_filters = []

            for arg in args:
                if arg.startswith("category:"):
                    category_filter = arg.split(":", 1)[1]
                elif arg.startswith("tag:"):
                    tag_filters.append(arg.split(":", 1)[1])

            if category_filter:
                rooms = await tag_service.find_rooms_by_category(session, category_filter)
            elif tag_filters:
                rooms = await tag_service.find_rooms_by_tags_all(session, tag_filters)

        # Formatear resultado
        output = f"🔍 <b>Salas encontradas ({len(rooms)}):</b>\n\n"
        for room in rooms[:20]:  # Límite de 20
            category_str = f" [cat: {room.category}]" if room.category else ""
            tags_str = f" [tags: {', '.join(room.tags)}]" if room.tags else ""
            output += f"• {room.name}{category_str}{tags_str}\n"

        await message.answer(output, parse_mode="HTML")

class CmdListItems(Command):
    """Lista items filtrados por category o tags."""
    # Similar a CmdListRooms pero para items
    pass

class CmdShowCategories(Command):
    """Muestra todas las categorías disponibles."""
    names = ["categorias", "categories"]
    lock = "role:ADMIN"
    description = "Muestra todas las categorías de rooms/items"

    async def execute(self, character, session, message, args):
        from src.services import tag_service

        room_cats = tag_service.get_all_categories_from_rooms()
        item_cats = tag_service.get_all_categories_from_items()

        output = "📂 <b>Categorías disponibles:</b>\n\n"
        output += "<b>Rooms:</b>\n" + "\n".join(f"  • {cat}" for cat in sorted(room_cats))
        output += "\n\n<b>Items:</b>\n" + "\n".join(f"  • {cat}" for cat in sorted(item_cats))

        await message.answer(output, parse_mode="HTML")

# Agregar a COMMAND_SETS en dispatcher
```

---

### Fase 2: Base de Datos + Prototipos (FUTURO)

**Solo implementar si Fase 1 se queda corta.**

**Ventajas adicionales:**
- ✅ Categories/Tags pueden cambiar dinámicamente en runtime
- ✅ Instancias individuales pueden tener categories/tags únicos
- ✅ Búsquedas SQL más eficientes (con índices)

**Desventajas:**
- ❌ Requiere migración de BD
- ❌ Más complejo de mantener
- ❌ Puede divergir de prototipos (confusión)

#### 2.1. Migración de Base de Datos

**Agregar columnas a `Room` y `Item`:**
```python
# En src/models/room.py
category = Column(String, nullable=True)  # Puede ser null
tags = Column(JSONB, nullable=False, default=list)  # Array de strings

# En src/models/item.py
category = Column(String, nullable=True)
tags = Column(JSONB, nullable=False, default=list)
```

**Migración Alembic:**
```bash
alembic revision --autogenerate -m "Add category and tags to Room and Item"
alembic upgrade head
```

#### 2.2. Métodos Híbridos

```python
# En src/models/room.py
def get_category(self) -> str | None:
    """Retorna category de BD si existe, sino del prototipo."""
    return self.category or self.prototype.get("category")

def get_tags(self) -> list[str]:
    """Retorna tags de BD si existen, sino del prototipo."""
    if self.tags:  # Si hay tags en BD
        return self.tags
    return self.prototype.get("tags", [])

def set_category(self, category: str | None):
    """Establece categoría (sobrescribe prototipo)."""
    self.category = category

def add_tag(self, tag: str):
    """Agrega un tag (preserva tags del prototipo + nuevos)."""
    current_tags = list(self.get_tags())
    if tag not in current_tags:
        current_tags.append(tag)
        self.tags = current_tags

def remove_tag(self, tag: str):
    """Remueve un tag."""
    current_tags = list(self.get_tags())
    if tag in current_tags:
        current_tags.remove(tag)
        self.tags = current_tags
```

#### 2.3. Comandos de Admin para Modificar

```python
class CmdSetCategory(Command):
    """Establece categoría de un objeto."""
    names = ["set_category"]
    lock = "role:ADMIN"

    async def execute(self, character, session, message, args):
        # /set_category room <room_id> <category>
        # /set_category item <item_id> <category>
        pass

class CmdAddTag(Command):
    """Agrega un tag a un objeto."""
    names = ["add_tag"]
    lock = "role:ADMIN"

    async def execute(self, character, session, message, args):
        # /add_tag room <room_id> <tag>
        # /add_tag item <item_id> <tag>
        pass
```

---

## 📚 Tareas de Documentación

### Actualizar `docs/`

1. **Crear `docs/03_ENGINE_SYSTEMS/08_CATEGORIES_AND_TAGS.md`**
   - Explicar el concepto de Categories y Tags
   - Diferencia entre Category (una) y Tags (múltiples)
   - Cómo se usan en prototipos
   - Casos de uso comunes
   - Referencia del `tag_service`

2. **Actualizar `docs/04_CONTENT_CREATION/02_CREATING_PROTOTYPES.md`**
   - Agregar sección sobre `category` y `tags`
   - Ejemplos prácticos de rooms e items con categories/tags
   - Mejores prácticas de nomenclatura
   - Cuándo usar category vs tags

3. **Actualizar `docs/05_ADMIN_GUIDE.md`**
   - Documentar comandos de búsqueda por category/tags
   - Ejemplos de uso de `/listar_rooms`, `/categorias`, etc.
   - Si se implementa Fase 2: comandos para modificar categories/tags

### Actualizar `README.md`

Agregar en la sección de **Features**:
- Sistema de Categories y Tags para organización de contenido
- Búsqueda y filtrado avanzado de rooms/items

### Actualizar `CLAUDE.md`

1. **Sección "Sistema de Categories y Tags"** en "Engine Systems":
   ```markdown
   ### Sistema de Categories y Tags

   Inspirado en Evennia, permite organizar y buscar contenido:
   - **Category**: Un objeto pertenece a UNA categoría (ej: "zona_bosque", "tipo_arma")
   - **Tags**: Un objeto puede tener MÚLTIPLES tags (ej: ["oscuro", "peligroso"])

   **Implementación:**
   - Definidos en prototipos (`category` y `tags` keys)
   - Accesibles vía properties en modelos
   - Servicio `tag_service` para búsquedas

   Ver: `docs/03_ENGINE_SYSTEMS/08_CATEGORIES_AND_TAGS.md`
   ```

2. **Agregar en "Creación de Contenido"**:
   - Ejemplos de cómo agregar category/tags a prototipos
   - Mejores prácticas de organización

---

## ✅ Checklist de Implementación

### Fase 1 (Prototipos)

- [ ] **1. Actualizar estructura de prototipos**
  - [ ] Agregar `category` y `tags` a `ROOM_PROTOTYPES`
  - [ ] Agregar `category` y `tags` a `ITEM_PROTOTYPES`
  - [ ] Categorizar salas existentes (ej: limbo → category:"inicio")
  - [ ] Categorizar items existentes (ej: espada → category:"arma")

- [ ] **2. Extender modelos con properties**
  - [ ] Agregar `@property category` a `Room`
  - [ ] Agregar `@property tags` a `Room`
  - [ ] Agregar `@property category` a `Item`
  - [ ] Agregar `@property tags` a `Item`

- [ ] **3. Crear `tag_service.py`**
  - [ ] Implementar `find_rooms_by_category()`
  - [ ] Implementar `find_rooms_by_tag()`
  - [ ] Implementar `find_rooms_by_tags_all()`
  - [ ] Implementar `find_rooms_by_tags_any()`
  - [ ] Implementar equivalentes para Items
  - [ ] Implementar funciones de utilidad (get_all_categories, etc.)

- [ ] **4. Comandos de Admin**
  - [ ] Crear `commands/admin/search.py`
  - [ ] Implementar `CmdListRooms`
  - [ ] Implementar `CmdListItems`
  - [ ] Implementar `CmdShowCategories`
  - [ ] Implementar `CmdShowTags`
  - [ ] Agregar comandos a `COMMAND_SETS` en dispatcher

- [ ] **5. Documentación**
  - [ ] Crear `docs/03_ENGINE_SYSTEMS/08_CATEGORIES_AND_TAGS.md`
  - [ ] Actualizar `docs/04_CONTENT_CREATION/02_CREATING_PROTOTYPES.md`
  - [ ] Actualizar `docs/05_ADMIN_GUIDE.md`
  - [ ] Actualizar `README.md`
  - [ ] Actualizar `CLAUDE.md`

- [ ] **6. Testing**
  - [ ] Probar búsqueda por categoría
  - [ ] Probar búsqueda por tags
  - [ ] Probar comandos de admin
  - [ ] Verificar que no rompe funcionalidad existente

### Fase 2 (Base de Datos) - OPCIONAL/FUTURO

- [ ] **1. Migración de BD**
  - [ ] Agregar columnas `category` y `tags` a Room
  - [ ] Agregar columnas `category` y `tags` a Item
  - [ ] Crear migración Alembic
  - [ ] Aplicar migración

- [ ] **2. Métodos híbridos**
  - [ ] Implementar `get_category()` / `set_category()`
  - [ ] Implementar `get_tags()` / `add_tag()` / `remove_tag()`

- [ ] **3. Comandos de modificación**
  - [ ] `CmdSetCategory`
  - [ ] `CmdAddTag`
  - [ ] `CmdRemoveTag`

- [ ] **4. Optimización de búsquedas**
  - [ ] Usar queries SQL directas en `tag_service`
  - [ ] Agregar índices en BD si es necesario

---

## 🎯 Casos de Uso Prácticos

### Organización de Zonas
```python
# Todas las salas del Bosque Oscuro
"claro_bosque_1": {
    "category": "el_bosque_oscuro",
    "tags": ["bosque", "exterior", "peligroso"]
}

# Todas las salas de la Ciudad
"plaza_central": {
    "category": "ciudad_runegard",
    "tags": ["ciudad", "seguro", "social"]
}
```

### Búsquedas de Items
```python
# Encontrar todas las armas
items = await tag_service.find_items_by_category(session, "arma")

# Encontrar items legendarios
items = await tag_service.find_items_by_tag(session, "legendario")

# Encontrar espadas legendarias
items = await tag_service.find_items_by_tags_all(session, ["espada", "legendario"])
```

### Sistema de Clima (Futuro)
```python
# Aplicar lluvia a todas las salas exteriores
outdoor_rooms = await tag_service.find_rooms_by_tag(session, "exterior")
for room in outdoor_rooms:
    apply_weather_effect(room, "lluvia")
```

### Quests Dinámicas (Futuro)
```python
# Quest: "Explora 5 salas del bosque oscuro"
bosque_rooms = await tag_service.find_rooms_by_category(session, "el_bosque_oscuro")
quest_progress = len(visited_rooms.intersection(bosque_rooms))
```

---

## 💡 Mejores Prácticas

### Nomenclatura de Categories
- **Lowercase con underscores**: `el_bosque_oscuro`, `ciudad_runegard`
- **Descriptivo pero conciso**: `arma`, `armadura`, `consumible`
- **Evitar duplicados**: Una jerarquía clara (zona > subzona si es necesario)

### Nomenclatura de Tags
- **Lowercase con underscores**: `bosque`, `peligroso`, `legendario`
- **Adjetivos o sustantivos**: `oscuro`, `exterior`, `arma`, `espada`
- **Específicos pero reutilizables**: `mágico` mejor que `encantado_con_fuego`
- **Evitar redundancia**: Si category es "arma", no necesitas tag "arma"

### Cuándo usar Category vs Tags
- **Category**: Para clasificación primaria/tipo principal
  - Zona geográfica de salas
  - Tipo de item (arma, armadura, consumible)
  - Facción de NPC

- **Tags**: Para características adicionales/múltiples
  - Ambiente (exterior, interior, oscuro, iluminado)
  - Dificultad (peligroso, seguro)
  - Propiedades (mágico, legendario, único)
  - Mecánicas (interactivo, scripted)

---

## 🚀 Próximos Pasos

1. **Empezar con Fase 1** (solo prototipos)
2. Implementar category/tags en 2-3 salas de prueba
3. Crear `tag_service.py` básico
4. Crear comando `/listar_rooms category:X`
5. Probar que funciona
6. Expandir a todas las salas/items existentes
7. Documentar en `docs/`
8. Solo pasar a Fase 2 si se necesita modificación dinámica

**Estimación de trabajo:** 4-6 horas para Fase 1 completa + documentación.
