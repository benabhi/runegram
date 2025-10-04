# Guía de Templates de Output

Esta guía explica cómo funciona el sistema de templates de Runegram, que permite separar la lógica de presentación del código y mantener formatos visuales consistentes en todos los comandos.

## ¿Qué es el Sistema de Templates?

El sistema de templates utiliza **Jinja2** para renderizar el output de los comandos. Esto significa que en lugar de tener HTML hardcodeado en cada comando, usamos plantillas que se pueden personalizar y reutilizar.

### Beneficios

1. **Consistencia Visual**: Todos los outputs siguen el mismo estilo y usan los mismos íconos
2. **Facilidad de Modificación**: Cambiar el formato de un comando es tan simple como editar un archivo template
3. **Personalización**: Los prototipos pueden definir templates personalizados
4. **Mantenibilidad**: Separación clara entre lógica de negocio y presentación
5. **Internacionalización Futura**: Base sólida para múltiples idiomas

## Estructura del Sistema

```
src/templates/
├── __init__.py            # Exports principales
├── template_engine.py     # Motor de renderizado Jinja2
├── icons.py              # Diccionario de íconos/emojis
└── base/                 # Templates base
    ├── room.html.j2
    ├── inventory.html.j2
    ├── character.html.j2
    ├── help.html.j2
    ├── item_look.html.j2
    └── who.html.j2
```

## Íconos Disponibles

El archivo `src/templates/icons.py` define todos los emojis utilizados en el juego:

| Categoría | Ejemplo | Descripción |
|-----------|---------|-------------|
| **Navegación** | 📍 🚪 ⬆️ ⬇️ ➡️ ⬅️ | Ubicaciones y direcciones |
| **Personajes** | 👤 🧑 🤖 👹 | Jugadores, NPCs, enemigos |
| **Items** | 📦 🎒 💎 🧳 🔑 💰 | Objetos y contenedores |
| **Equipamiento** | ⚔️ 🗡️ 🛡️ ⛑️ 💍 | Armas y armaduras |
| **Acciones** | 👁️ 🤲 📤 🔧 🔓 | Comandos y acciones |
| **Combate** | ⚔️ 🛡️ ✨ 💥 💀 | Batalla y daño |
| **Sistema** | ❓ ℹ️ ⚠️ ❌ ✅ | Mensajes de sistema |

**Ver la lista completa en**: `src/templates/icons.py`

### Usar Íconos en Templates

```jinja
{# En un template #}
{{ icon('room') }} <b>{{ room.name }}</b>
{{ icon('inventory') }} <b>Inventario</b>
{{ icon('weapon') }} Espada de hierro
```

### Usar Íconos en Código Python

```python
from src.templates import ICONS

message = f"{ICONS['room']} {room.name}"
```

## Personalizar Prototipos

Los prototipos pueden definir íconos personalizados y templates específicos usando el campo `display`.

### Ejemplo: Prototipo de Sala

```python
# En game_data/room_prototypes.py

ROOM_PROTOTYPES = {
    "plaza_central": {
        "name": "Plaza Central de Runegard",
        "description": "Estás en el corazón de la ciudad...",
        "exits": {
            "norte": "calle_mercaderes",
            "sur": "limbo"
        },
        "display": {
            "icon": "🏛️",                    # Ícono personalizado
            "template": "custom_plaza.html.j2"  # Template personalizado (opcional)
        }
    }
}
```

### Ejemplo: Prototipo de Item

```python
# En game_data/item_prototypes.py

ITEM_PROTOTYPES = {
    "espada_viviente": {
        "name": "una espada viviente",
        "description": "La hoja de acero parece retorcerse...",
        "display": {
            "icon": "⚔️",  # Se muestra en inventarios y listados
        }
    },

    "mochila_cuero": {
        "name": "una mochila de cuero",
        "description": "Una mochila simple...",
        "is_container": True,
        "display": {
            "icon": "🎒",
        }
    }
}
```

## Templates Base Disponibles

### 1. room.html.j2

Renderiza la descripción de una sala con:
- Ícono y nombre de la sala
- Descripción
- Items en la sala
- Personajes presentes
- Salidas disponibles

**Uso:**
```python
from src.utils.presenters import format_room

formatted = await format_room(room, viewing_character=character)
```

### 2. inventory.html.j2

Muestra el inventario de un personaje o el contenido de un contenedor.

**Uso:**
```python
from src.utils.presenters import format_inventory

# Inventario personal
formatted = format_inventory(character.items)

# Contenedor
formatted = format_inventory(container.contained_items, owner_name=container.get_name(), is_container=True)
```

### 3. character.html.j2

Muestra la hoja de personaje con información básica.

**Uso:**
```python
from src.utils.presenters import format_character

formatted = format_character(character)
```

### 4. item_look.html.j2

Describe un objeto cuando se mira en detalle.

**Uso:**
```python
from src.utils.presenters import format_item_look

formatted = format_item_look(item, can_interact=True)
```

### 5. who.html.j2

Lista de jugadores conectados.

**Uso:**
```python
from src.utils.presenters import format_who_list

formatted = format_who_list(online_characters, viewer_character=character)
```

## Sistema de Límites y Paginación

Para evitar outputs abrumadores en dispositivos móviles cuando hay listas largas (ej: 500 items), Runegram implementa un sistema híbrido de límites y paginación.

### Límites de Visualización

Los templates base truncan automáticamente listas largas usando configuraciones en `src/config.py`:

```python
# Configuración en src/config.py
class Settings(BaseSettings):
    max_room_items_display: int = 10
    max_room_characters_display: int = 10
    max_inventory_display: int = 15
    max_container_display: int = 15
    max_who_display: int = 20
```

**Ejemplo de output truncado:**

```
🎒 Cosas a la vista:
- 📦 una caja de madera
- 🔑 una llave oxidada
- 💎 una gema brillante
... (10 items mostrados)

... y 490 items más en el suelo.
Usa /items para ver la lista completa.
```

### Comandos con Paginación

Para explorar listas completas, Runegram provee comandos especializados:

#### 1. /items [página]

Lista todos los items de la sala con paginación (30 items por página).

```
/items        # Primera página
/items 2      # Segunda página
```

#### 2. /personajes [página]

Lista todos los personajes en la sala con paginación.

```
/personajes
/personajes 2
```

#### 3. /inventario todo [página]

Muestra el inventario completo sin límites.

```
/inv todo     # Primera página
/inv todo 3   # Tercera página
```

#### 4. /quien todo [página]

Lista completa de jugadores conectados.

```
/quien todo
/quien todo 2
```

### Implementar Paginación en Comandos Personalizados

**Paso 1: Usar el helper de paginación**

```python
from src.utils.pagination import paginate_list, format_pagination_footer

async def execute(self, character, session, message, args):
    # Obtener número de página
    page = 1
    if args:
        try:
            page = int(args[0])
        except ValueError:
            await message.answer("Uso: /micomando [número de página]")
            return

    # Obtener items
    items = get_my_items()

    # Paginar
    pagination = paginate_list(items, page=page, per_page=30)

    # Construir output
    lines = [
        f"{ICONS['item']} <b>Mis Items</b>",
        "─────────────────────────────"
    ]

    for idx, item in enumerate(pagination['items'], start=pagination['start_index']):
        lines.append(f"{idx}. {item.name}")

    # Agregar footer de paginación
    if pagination['total_pages'] > 1:
        lines.append(format_pagination_footer(
            pagination['page'],
            pagination['total_pages'],
            '/micomando',
            pagination['total_items']
        ))

    output = "<pre>" + "\n".join(lines) + "</pre>"
    await message.answer(output, parse_mode="HTML")
```

**Paso 2: Metadata de paginación**

La función `paginate_list()` retorna:

```python
{
    'items': [...]            # Slice de items para esta página
    'page': 2,                # Página actual
    'total_pages': 5,         # Total de páginas
    'total_items': 127,       # Total de items
    'has_next': True,         # ¿Hay página siguiente?
    'has_prev': True,         # ¿Hay página anterior?
    'start_index': 31,        # Índice del primer item (1-indexed)
    'end_index': 60           # Índice del último item (1-indexed)
}
```

### Personalizar Límites en Presenters

Los presenters aceptan parámetros opcionales para anular límites:

```python
from src.utils.presenters import format_room

# Usar límites por defecto
formatted = await format_room(room, viewing_character=character)

# Límites personalizados
formatted = await format_room(
    room,
    viewing_character=character,
    max_items=5,          # Solo mostrar 5 items
    max_characters=3      # Solo mostrar 3 personajes
)

# Sin límites (mostrar todo)
formatted = await format_room(
    room,
    viewing_character=character,
    max_items=999999,
    max_characters=999999
)
```

### Footer de Paginación Estándar

El footer se genera automáticamente:

```
Página 2 de 5 (127 items totales)
Usa /items 3 para siguiente | /items 1 para anterior.
```

### Mejores Prácticas para Listas

1. **Listas pequeñas (< 20 items)**: Mostrar todo directamente
2. **Listas medianas (20-50 items)**: Usar límites con mensaje de truncado
3. **Listas grandes (> 50 items)**: Ofrecer comando dedicado con paginación
4. **Siempre**: Indicar al jugador cómo ver más items

**Ejemplo ideal:**

```python
if len(items) <= 20:
    # Mostrar todo
    format_inventory(items)
else:
    # Mostrar con límite
    format_inventory(items, max_display=15)
    # El template automáticamente muestra: "... y X items más"
```

## Crear Templates Personalizados

### Paso 1: Crear el Archivo Template

Crea un archivo `.html.j2` en `src/templates/base/`:

```jinja
{# src/templates/base/my_custom.html.j2 #}
<pre>{{ icon('custom') }} <b>{{ title }}</b>
{{ description }}

{% if items %}
{{ icon('item') }} <b>Items:</b>
{%- for item in items %}
- {{ item.name }}
{%- endfor %}
{%- endif %}</pre>
```

### Paso 2: Usar el Template en un Comando

```python
from src.templates import render_template

async def execute(self, character, session, message, args):
    context = {
        'title': 'Mi Comando',
        'description': 'Descripción personalizada',
        'items': some_items_list,
        'icon': lambda key: ICONS.get(key, '')
    }

    output = render_template('my_custom.html.j2', **context)
    await message.answer(output, parse_mode="HTML")
```

## Estándares de Formato

Para mantener consistencia, todos los templates deben seguir estos principios:

### 1. Estructura Visual

```
[ÍCONO] [TÍTULO EN NEGRITA]
[Descripción de 1-3 líneas]

[ÍCONO] [SECCIÓN]:
- Item 1
- Item 2

[ÍCONO] [SALIDAS/ACCIONES]:
⬆️ Norte
➡️ Este
```

### 2. Uso de Íconos

- **Siempre** usa íconos al inicio de cada sección
- Un ícono por concepto (no reutilices para cosas diferentes)
- Usa íconos de dirección (⬆️ ⬇️ ➡️ ⬅️) para salidas

### 3. Formato de Texto

- Títulos en `<b>negrita</b>`
- Narración/ambiente en texto normal
- Diálogos/emotes en `<i>cursiva</i>`
- Todo envuelto en `<pre>` para formato monoespaciado

### 4. Listas

**Regla de Indentación (Filosofía de Diseño):**
- **TODOS** los ítems en listas **DEBEN** estar indentados con **4 espacios** + guion
- Esta es una regla universal que aplica a todos los templates
- Los 4 espacios simulan un tab y mejoran la legibilidad en Telegram

**Formato estándar de listas:**
```
[ÍCONO] [TÍTULO]:
    - Item 1
    - Item 2
    - Item 3
```

**Ejemplo real:**
```
👁️ Cosas a la vista:
    - 🎒 una mochila de cuero
    - ⚔️ una espada viviente

🚪 Salidas:
    - ⬆️ Norte (Plaza Central)
    - ⬇️ Sur (El Limbo)
```

**Reglas adicionales:**
- Usar guiones (`-`) obligatoriamente para cada ítem
- Máximo 3 líneas de descripción antes de listas
- Números en formato `X/Y` (ej: `32/40` vida)
- La indentación de 4 espacios es consistente en TODOS los templates

## Sintaxis Jinja2 Útil

### Variables
```jinja
{{ variable }}
{{ object.property }}
{{ dictionary.get('key', 'default') }}
```

### Condicionales
```jinja
{% if condition %}
  Contenido si verdadero
{% elif other_condition %}
  Contenido alternativo
{% else %}
  Contenido por defecto
{% endif %}
```

### Loops
```jinja
{% for item in items %}
- {{ item.name }}
{% endfor %}

{# Con contador #}
{% for item in items %}
{{ loop.index }}. {{ item.name }}
{% endfor %}
```

### Filtros
```jinja
{{ text|capitalize }}
{{ items|length }}
{{ items|sort(attribute='name') }}
{{ count|pluralize('item', 'items') }}
```

### Funciones Helper
```jinja
{{ icon('room') }}                    {# Obtener ícono por clave #}
{{ get_direction_icon('norte') }}     {# Ícono de dirección #}
```

## Mejores Prácticas

1. **Usar presenters**: En lugar de llamar `render_template` directamente, usa las funciones en `src/utils/presenters.py`

2. **Cargar relaciones**: Asegúrate de cargar las relaciones de SQLAlchemy antes de pasar objetos a templates
   ```python
   await session.refresh(item, attribute_names=['contained_items'])
   ```

3. **Manejar errores**: Los presenters ya incluyen try/except, pero asegúrate de validar datos
   ```python
   if not character.room:
       return "Estás en el vacío."
   ```

4. **Consistencia de íconos**: Usa siempre las constantes de `ICONS`, no hardcodees emojis

5. **Templates simples**: Mantén la lógica en Python, los templates solo deben formatear

## Ejemplos Completos

### Ejemplo 1: Comando Personalizado con Template

```python
# En commands/player/custom.py

from src.templates import render_template, ICONS

class CmdInspect(Command):
    names = ["inspeccionar", "inspect"]
    description = "Inspecciona un objeto en detalle"

    async def execute(self, character, session, message, args):
        if not args:
            await message.answer("¿Qué quieres inspeccionar?")
            return

        item_name = " ".join(args).lower()
        item = find_item(item_name, character)

        if not item:
            await message.answer(f"No encuentras '{item_name}'.")
            return

        context = {
            'item': item,
            'character': character,
            'icon': lambda key: ICONS.get(key, '')
        }

        output = render_template('item_look.html.j2', **context)
        await message.answer(output, parse_mode="HTML")
```

### Ejemplo 2: Template Personalizado para Sala Especial

```python
# En game_data/room_prototypes.py

ROOM_PROTOTYPES = {
    "throne_room": {
        "name": "Sala del Trono",
        "description": "Un majestuoso salón real...",
        "display": {
            "icon": "👑",
            "template": "throne_room.html.j2"  # Template personalizado
        }
    }
}
```

```jinja
{# src/templates/base/throne_room.html.j2 #}
<pre>👑 <b>{{ room.name }}</b>
<i>{{ room.description }}</i>

✨ <b>El Trono Resplandece</b>
Un trono de oro macizo domina la sala.

{% if room.characters %}
👥 <b>Presentes ante el trono:</b>
{%- for char in room.characters %}
- {{ char.name }}
{%- endfor %}
{% endif %}

🚪 <b>Salidas:</b>
{%- for exit in room.exits_from %}
{{ get_direction_icon(exit.name) }} {{ exit.name|capitalize }}
{%- endfor %}</pre>
```

## Resolución de Problemas

### El template no se encuentra

```
Error: Template 'my_template.html.j2' no encontrado
```

**Solución**: Verifica que el archivo existe en `src/templates/base/` con extensión `.html.j2`

### Error de sintaxis en template

```
TemplateSyntaxError: unexpected '}'
```

**Solución**: Revisa la sintaxis Jinja2. Recuerda:
- Variables: `{{ }}`
- Bloques: `{% %}`
- Comentarios: `{# #}`

### Íconos no se muestran

**Solución**: Asegúrate de pasar la función `icon` en el contexto:
```python
context = {
    'icon': lambda key: ICONS.get(key, ''),
    # ... otros datos
}
```

### Relaciones no cargadas (lazy loading)

```
MissingGreenlet error
```

**Solución**: Carga las relaciones explícitamente con `selectinload` o `refresh`:
```python
await session.refresh(object, attribute_names=['relation_name'])
```

---

Con este sistema de templates, Runegram mantiene una presentación visual consistente, profesional y fácilmente personalizable. ¡Disfruta creando comandos con outputs hermosos!
