# Sistema de Categories y Tags

## 📋 Visión General

El sistema de **Categories y Tags** permite organizar y buscar contenido (Rooms, Items) de forma eficiente. Inspirado en **Evennia**, el framework de MUDs más popular de Python.

### Conceptos Clave

- **Category (Categoría)**: Un objeto pertenece a **UNA** categoría
  - Ejemplos: `"ciudad_runegard"`, `"arma"`, `"consumible"`
  - Clasificación principal/tipo del objeto

- **Tags (Etiquetas)**: Un objeto puede tener **MÚLTIPLES** tags
  - Ejemplos: `["exterior", "seguro"]`, `["espada", "magica", "unica"]`
  - Características o propiedades adicionales

## 🎯 Beneficios

1. **Búsquedas Potentes**: Encuentra rápidamente grupos de objetos
2. **Organización**: Agrupa contenido por zonas, tipos, características
3. **Sistemas Futuros**: Base para clima, quests, spawn de mobs, eventos
4. **Balanceo**: Identifica fácilmente items para ajustar stats

## 🛠️ Implementación

### Fase 1: Prototipos (Actual)

Categories y tags se definen en los **prototipos** (`game_data/`).

**Ventajas:**
- ✅ Simple, sin cambios en BD
- ✅ Todo en archivos de contenido
- ✅ Fácil de mantener

**Limitación:**
- ❌ No se pueden cambiar dinámicamente en runtime
- ❌ Todos los objetos del mismo prototipo comparten category/tags

### Definir en Prototipos

**`game_data/room_prototypes.py`:**
```python
"plaza_central": {
    "name": "Plaza Central de Runegard",
    "description": "...",
    "category": "ciudad_runegard",  # UNA categoría
    "tags": ["ciudad", "seguro", "social", "exterior"],  # MÚLTIPLES tags
    "exits": {...}
}
```

**`game_data/item_prototypes.py`:**
```python
"espada_viviente": {
    "name": "una espada viviente",
    "description": "...",
    "category": "arma",  # Tipo de item
    "tags": ["espada", "magica", "unica", "una_mano"],  # Características
    "keywords": [...]
}
```

### Acceso desde Código

Los modelos `Room` e `Item` tienen properties para acceder:

```python
# En src/models/room.py
@property
def category(self) -> str | None:
    """Retorna la categoría desde el prototipo."""
    return self.prototype.get("category")

@property
def tags(self) -> list[str]:
    """Retorna los tags desde el prototipo."""
    return self.prototype.get("tags", [])
```

**Uso:**
```python
if room.category == "ciudad_runegard":
    # Aplicar lógica específica de ciudad
    pass

if "exterior" in room.tags:
    # Aplicar efectos de clima
    pass
```

## 🔍 Servicio tag_service.py

Módulo centralizado para búsquedas.

### Búsquedas de Rooms

```python
from src.services import tag_service

# Por categoría
rooms = await tag_service.find_rooms_by_category(session, "ciudad_runegard")

# Por tag único
rooms = await tag_service.find_rooms_by_tag(session, "exterior")

# Por TODOS los tags (AND)
rooms = await tag_service.find_rooms_by_tags_all(session, ["bosque", "peligroso"])

# Por AL MENOS UN tag (OR)
rooms = await tag_service.find_rooms_by_tags_any(session, ["ciudad", "pueblo"])
```

### Búsquedas de Items

```python
# Por categoría
items = await tag_service.find_items_by_category(session, "arma")

# Por tag
items = await tag_service.find_items_by_tag(session, "magica")

# Por múltiples tags
items = await tag_service.find_items_by_tags_all(session, ["espada", "legendaria"])
```

### Funciones de Utilidad

```python
# Obtener todas las categorías
room_categories = tag_service.get_all_categories_from_rooms()
item_categories = tag_service.get_all_categories_from_items()

# Obtener todos los tags
room_tags = tag_service.get_all_tags_from_rooms()
item_tags = tag_service.get_all_tags_from_items()
```

## 💻 Comandos de Admin

### /listarsalas (extendido)

El comando existente `/listarsalas` ahora soporta filtrado por categoría y tags:

```bash
# Todas las salas (uso original)
/listarsalas

# Filtrar por categoría
/listarsalas cat:ciudad_runegard

# Filtrar por tag
/listarsalas tag:exterior

# Filtrar por múltiples tags
/listarsalas tag:exterior,seguro,social
```

Alias: `/lsalas`

**Sintaxis de filtros:**
- `cat:X` - Filtra por categoría X
- `tag:Y,Z` - Filtra por tags Y y Z (separados por coma, lógica AND)

### /listaritems

```bash
# Todos los items
/listaritems

# Filtrar por categoría
/listaritems cat:arma

# Filtrar por tag
/listaritems tag:magica

# Filtrar por múltiples tags
/listaritems tag:magica,unica
```

Alias: `/litems`

**Sintaxis de filtros:**
- `cat:X` - Filtra por categoría X
- `tag:Y,Z` - Filtra por tags Y y Z (separados por coma, lógica AND)

### /listarcategorias

Muestra todas las categorías disponibles de salas e items.

Alias: `/cats`, `/lcats`

### /listartags

Muestra todos los tags disponibles de salas e items.

Alias: `/etiquetas`, `/ltags`

## 💡 Mejores Prácticas

### Nomenclatura de Categories

- **Lowercase con underscores**: `el_bosque_oscuro`, `ciudad_runegard`
- **Descriptivo pero conciso**: `arma`, `armadura`, `consumible`
- **Evitar duplicados**: Jerarquía clara

### Nomenclatura de Tags

- **Lowercase con underscores**: `bosque`, `peligroso`, `legendario`
- **Adjetivos o sustantivos**: `oscuro`, `exterior`, `magico`
- **Específicos pero reutilizables**: `magico` > `encantado_con_fuego`
- **Sin redundancia**: Si category es "arma", no necesitas tag "arma"

### Cuándo usar Category vs Tags

**Category** (clasificación principal):
- Zona geográfica de salas
- Tipo de item (arma, armadura, consumible)
- Facción de NPC

**Tags** (características adicionales):
- Ambiente (exterior, interior, oscuro)
- Dificultad (peligroso, seguro)
- Propiedades (magico, legendario, unico)
- Mecánicas (interactivo, scripted)

## 🎯 Casos de Uso

### Organización de Zonas

```python
# Todas las salas del Bosque Oscuro
"claro_1": {
    "category": "el_bosque_oscuro",
    "tags": ["bosque", "exterior", "peligroso"]
}

# Todas las salas de la Ciudad
"plaza": {
    "category": "ciudad_runegard",
    "tags": ["ciudad", "seguro", "social"]
}
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
quest_progress = len(visited_rooms.intersection(set(r.id for r in bosque_rooms)))
```

### Spawn de Enemigos (Futuro)

```python
# Spawnear enemigos solo en salas peligrosas
dangerous_rooms = await tag_service.find_rooms_by_tag(session, "peligroso")
for room in dangerous_rooms:
    spawn_enemy(room, enemy_type="goblin")
```

### Balanceo de Items

```python
# Encontrar todas las armas para ajustar daño
weapons = await tag_service.find_items_by_category(session, "arma")
for weapon in weapons:
    # Ajustar stats según balance
    adjust_weapon_stats(weapon)
```

## 🚀 Fase 2 (Futuro - Opcional)

Si se necesita modificación dinámica:

- Agregar columnas `category` y `tags` a BD (Room, Item)
- Métodos híbridos (BD sobrescribe prototipo)
- Comandos admin para modificar categories/tags en runtime

**Solo implementar si Fase 1 se queda corta.**

## 📚 Referencias

- **Evennia Tags Documentation**: https://www.evennia.com/docs/latest/Components/Tags.html
- **tag_service.py**: `src/services/tag_service.py`
- **Comandos de búsqueda**: `commands/admin/search.py`
- **Prototipos**: `game_data/room_prototypes.py`, `game_data/item_prototypes.py`
