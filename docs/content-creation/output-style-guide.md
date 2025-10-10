---
título: "Guía de Estilo de Outputs de Runegram"
categoría: "Creación de Contenido"
audiencia: "creador-de-contenido, desarrollador"
versión: "2.0"
última_actualización: "2025-01-09"
autor: "Proyecto Runegram"
etiquetas: ["outputs", "templates", "jinja2", "formato", "UX", "telegram"]
documentos_relacionados:
  - "content-creation/creating-commands.md"
  - "getting-started/core-philosophy.md"
referencias_código:
  - "src/templates/"
  - "src/utils/presenters.py"
  - "src/templates/icons.py"
estado: "actual"
importancia: "crítica"
---

# Guía de Estilo de Outputs de Runegram

El objetivo de esta guía es asegurar que todos los mensajes que el jugador recibe sean claros, consistentes y estén optimizados para la lectura en dispositivos móviles a través de Telegram.

## Filosofía de Diseño

> **"Cada mensaje tiene un propósito específico y debe comunicarlo claramente."**

Runegram clasifica todos los outputs en **4 categorías principales**, cada una con su propio formato y propósito específico. Esta separación no es solo estilística, sino que refleja el **flujo de información** del juego.

---

## Las 4 Categorías de Outputs (CRÍTICO)

### 1. Outputs Descriptivos (La "Vista Principal")

Son los mensajes que describen el estado del mundo, el inventario, o listados de información. Son el pilar de la interfaz del juego.

**Comandos de Ejemplo:** `/mirar`, `/inventario`, `/quien`, `/ayuda`, `/personajes`, `/items`, y todos los comandos de listado de administrador (`/listarsalas`, etc.).

**Filosofía:** *"Un panel de información estructurado"*. Deben ser ricos en detalles pero fáciles de escanear visualmente.

#### Reglas de Formato

1. **Contenedor Principal:** **SIEMPRE** deben estar envueltos en etiquetas `<pre>...</pre>`. Esto asegura una fuente monoespaciada, preserva la indentación y mejora drásticamente la legibilidad.

2. **Títulos y Secciones:**
   - El título principal **SIEMPRE** comienza con un ícono, seguido de un espacio, y el texto en `<b>negrita y MAYÚSCULAS</b>`.
     ```html
     ✅ Correcto: <pre>📦 <b>TU INVENTARIO</b></pre>
     ❌ Incorrecto: <pre>📦 <b>Tu Inventario</b></pre>
     ```
   - Las sub-secciones siguen el mismo patrón: `[ÍCONO] <b>[Nombre de Sección]:</b>`.
     ```html
     ✅ Correcto: 🚪 <b>Salidas:</b>
     ```

3. **Listas (CRÍTICO - Regla Universal):**
   - **TODA** lista de elementos (objetos, personajes, salidas, etc.) **DEBE** estar indentada con **4 espacios**, seguidos de un guion y un espacio (`    - `).
   - Esta regla es **universal y no negociable**. Simula un `tab` y es la clave de la legibilidad en Telegram.
   - **NO usar tabs literales** (se renderizan como 1 espacio en Telegram)

   ```html
   ✅ Correcto:
   <pre>
   👁️ <b>Cosas a la vista:</b>
       - ⚔️ una espada oxidada
       - 🎒 una mochila de cuero
   </pre>
   ```

   ```html
   ❌ Incorrecto:
   <pre>
   👁️ <b>Cosas a la vista:</b>
   - ⚔️ una espada oxidada
   - 🎒 una mochila de cuero
   </pre>
   ```

4. **Íconos:**
   - Se usan para dar contexto visual rápido a títulos y secciones.
   - Deben provenir de la constante `ICONS` en `src/templates/icons.py` para mantener la consistencia.
   - No se usan para cada ítem de una lista, solo para las cabeceras.

#### Ejemplo Completo de Output Descriptivo

```html
<pre>🏛️ <b>PLAZA CENTRAL DE RUNEGARD</b>
Estás en el corazón de la ciudad. Una gran fuente de mármol domina el centro de la plaza.

👁️ <b>Cosas a la vista:</b>
    1. ⚔️ una espada oxidada
    2. 🎒 una mochila de cuero
    3. 💎 una gema brillante

👤 <b>Personajes:</b>
    - 👤 Gandalf
    - 👤 Aragorn

🚪 <b>Salidas:</b>
    - ⬆️ Norte (Calle de los Mercaderes)
    - ⬇️ Sur (El Templo Antiguo)
    - ➡️ Este (La Forja del Enano)</pre>
```

---

### 2. Notificaciones Sociales (Broadcasts)

Son mensajes que informan al jugador sobre acciones visibles realizadas por otros personajes en la misma sala.

**Eventos de Ejemplo:** Un jugador se mueve (`/norte`), coge o deja un objeto (`/coger`, `/dejar`), o realiza una emoción (`/emocion`).

**Filosofía:** *"El murmullo del mundo"*. Deben ser discretos y no interrumpir el flujo principal de información.

#### Reglas de Formato

1. **Contenedor:** **NUNCA** usan `<pre>`.
2. **Formato de Texto:** **SIEMPRE** están envueltos en etiquetas `<i>...</i>` (cursiva).
3. **Íconos:** **NUNCA** llevan íconos.
4. **Contenido:** Describen una acción en tercera persona.

#### Ejemplos

```html
<i>Gandalf se ha ido hacia el norte.</i>
<i>Aragorn ha cogido una espada del suelo.</i>
<i>Frodo se rasca la nariz.</i>
<i>Legolas ha dejado una mochila en el suelo.</i>
```

---

### 3. Notificaciones Directas y Privadas

Son mensajes dirigidos específicamente a un jugador, como resultado de una acción de otro o del sistema.

**Eventos de Ejemplo:** Recibir un susurro (`/susurrar`), recibir un objeto de otro jugador (`/dar`), mensajes de reconexión.

**Filosofía:** *"Un mensaje al oído"*. Deben sentirse personales y directos.

#### Reglas de Formato

1. **Contenedor:** **NUNCA** usan `<pre>`.
2. **Formato de Texto:** **SIEMPRE** están envueltos en etiquetas `<i>...</i>` (cursiva).
3. **Íconos:** **NUNCA** llevan íconos.
4. **Contenido:** Describen una acción en segunda persona ("te") o citan directamente.

#### Ejemplos

```html
<i>Gandalf te susurra: "Encuéntrame en la posada."</i>
<i>Aragorn te da una poción de vida.</i>
<i>Te has reconectado al juego.</i>
<i>Legolas te ha dado: una flecha élfica.</i>
```

---

### 4. Feedback de Acción y Errores

Son respuestas directas e inmediatas a un comando ejecutado por el propio jugador. Confirman el éxito, el fracaso o un error.

**Eventos de Ejemplo:** "Has cogido una espada", "No ves eso por aquí", "Uso: /comando [argumento]".

**Filosofía:** *"Respuesta del sistema"*. Deben ser concisos, claros y directos.

#### Reglas de Formato

1. **Contenedor:** **NUNCA** usan `<pre>`, **a menos que** el mensaje sea una lista o una estructura compleja (como un mensaje de desambiguación).

2. **Formato de Texto:** Texto plano, sin formato especial. Se puede usar `<b>` para resaltar partes clave si es necesario.

3. **Íconos:** **PUEDEN** usar un ícono al principio para indicar el resultado (✅, ❌, ❓, ⚠️).

#### Ejemplos

```html
Has cogido: una espada oxidada.
Dejas caer una poción de vida.
No ves a nadie con ese nombre por aquí.
❌ Ocurrió un error inesperado.
✅ Has activado el canal de Novatos.
```

#### Ejemplo de Feedback Complejo (con `<pre>`)

Cuando el feedback es una lista de opciones (como desambiguación):

```html
<pre>❓ Hay 2 'espada'. ¿Cuál quieres coger?

1. ⚔️ espada oxidada
2. ⚔️ espada brillante

Usa:
/coger 1.espada
/coger 2.espada</pre>
```

---

## Sistema de Templates Jinja2

Runegram utiliza **Jinja2** para renderizar el output de los comandos. Esto significa que en lugar de tener HTML hardcodeado en cada comando, usamos plantillas que se pueden personalizar y reutilizar.

### Beneficios

1. **Consistencia Visual**: Todos los outputs siguen el mismo estilo y usan los mismos íconos
2. **Facilidad de Modificación**: Cambiar el formato de un comando es tan simple como editar un archivo template
3. **Personalización**: Los prototipos pueden definir templates personalizados
4. **Mantenibilidad**: Separación clara entre lógica de negocio y presentación
5. **Internacionalización Futura**: Base sólida para múltiples idiomas

### Estructura del Sistema

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

### Íconos Disponibles

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

**Regla Universal:** Siempre usar `ICONS` de `src/templates/icons.py`, NO hardcodear emojis.

---

## Templates Base Disponibles

Runegram incluye templates pre-construidos para los comandos más comunes. Usa funciones centralizadas en `src/utils/presenters.py` para acceder a ellos.

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

---

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

---

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

### Personalizar Prototipos

Los prototipos pueden definir íconos personalizados y templates específicos usando el campo `display`.

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

---

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

---

## Reglas Universales de Formato

### 1. Indentación de Listas

**LA REGLA MÁS IMPORTANTE DE TODA LA GUÍA:**

- **TODA** lista en un output descriptivo (`<pre>`) **DEBE** usar **4 espacios + guion** (`    - `)
- Esta regla aplica a **TODOS** los templates sin excepción
- Los 4 espacios simulan un tab y son críticos para la legibilidad en Telegram
- **NO usar tabs literales** (se renderizan incorrectamente)

```html
✅ Correcto (4 espacios):
<pre>
👁️ <b>Items:</b>
    - ⚔️ espada
    - 🎒 mochila
</pre>
```

```html
❌ Incorrecto (sin indentación):
<pre>
👁️ <b>Items:</b>
- ⚔️ espada
- 🎒 mochila
</pre>
```

```html
❌ Incorrecto (tab literal):
<pre>
👁️ <b>Items:</b>
	- ⚔️ espada
	- 🎒 mochila
</pre>
```

### 2. Títulos en Mayúsculas

Todos los títulos principales deben estar en **MAYÚSCULAS**:

```html
✅ Correcto: 📦 <b>TU INVENTARIO</b>
✅ Correcto: 🏛️ <b>PLAZA CENTRAL</b>
✅ Correcto: 👤 <b>JUGADORES EN RUNEGRAM</b>

❌ Incorrecto: 📦 <b>Tu Inventario</b>
❌ Incorrecto: 🏛️ <b>Plaza Central</b>
```

### 3. Sub-secciones con Dos Puntos

Las sub-secciones siempre terminan con dos puntos `:`:

```html
✅ Correcto: 🚪 <b>Salidas:</b>
✅ Correcto: 👁️ <b>Cosas a la vista:</b>
✅ Correcto: 👤 <b>Personajes:</b>
```

### 4. Íconos desde Constantes

Siempre usar `ICONS` de `src/templates/icons.py`, NO hardcodear emojis:

```python
# ✅ Correcto
from src.templates import ICONS
message = f"{ICONS['room']} {room.name}"

# ❌ Incorrecto
message = f"🏛️ {room.name}"  # Hardcodeado
```

```jinja
{# ✅ Correcto en templates #}
{{ icon('room') }} <b>{{ room.name }}</b>

{# ❌ Incorrecto #}
🏛️ <b>{{ room.name }}</b>
```

---

## Implementación en Código

### En Templates Jinja2

```jinja
{# src/templates/base/example.html.j2 #}
<pre>{{ icon('inventory') }} <b>TU INVENTARIO</b>
{%- if not items %}
No llevas nada.
{%- else %}

👁️ <b>Items:</b>
{%- for item in items %}
    {{ loop.index }}. {{ item.get_name() }}
{%- endfor %}
{%- endif %}</pre>
```

### En Código Python

```python
from src.templates import ICONS

# Output Descriptivo
output = f"""<pre>{ICONS['room']} <b>{room.name.upper()}</b>
{room.description}

{ICONS['exit']} <b>Salidas:</b>
    - ⬆️ Norte
    - ⬇️ Sur</pre>"""

# Notificación Social (broadcast)
broadcast_msg = f"<i>{character.name} ha cogido una espada.</i>"

# Notificación Privada
private_msg = f"<i>{sender.name} te susurra: \"{message}\"</i>"

# Feedback Simple
feedback = "Has cogido: una espada oxidada."

# Feedback de Error
error = "❌ No ves ese objeto por aquí."
```

---

## Checklist de Validación

Antes de implementar un output, verifica:

**Para Outputs Descriptivos (`/mirar`, `/inventario`, etc.):**
- [ ] ¿Está envuelto en `<pre>...</pre>`?
- [ ] ¿El título está en MAYÚSCULAS con ícono y negrita?
- [ ] ¿Las listas usan **4 espacios + guion** (no tabs)?
- [ ] ¿Las sub-secciones tienen ícono, negrita y dos puntos?
- [ ] ¿Los íconos vienen de `ICONS` y no están hardcodeados?

**Para Notificaciones Sociales (broadcasts):**
- [ ] ¿Está envuelto en `<i>...</i>`?
- [ ] ¿NO usa `<pre>`?
- [ ] ¿NO tiene íconos?
- [ ] ¿Describe la acción en tercera persona?

**Para Notificaciones Privadas:**
- [ ] ¿Está envuelto en `<i>...</i>`?
- [ ] ¿NO usa `<pre>`?
- [ ] ¿NO tiene íconos?
- [ ] ¿Usa segunda persona ("te") o cita directa?

**Para Feedback de Acciones:**
- [ ] ¿Es texto plano (sin `<pre>`) a menos que sea lista?
- [ ] ¿Usa ícono de estado (✅❌❓⚠️) si es apropiado?
- [ ] ¿Es conciso y claro?

---

## Errores Comunes y Cómo Evitarlos

### ❌ Error 1: Usar `<pre>` en notificaciones sociales

```html
❌ Incorrecto:
<pre><i>Gandalf se ha ido hacia el norte.</i></pre>

✅ Correcto:
<i>Gandalf se ha ido hacia el norte.</i>
```

### ❌ Error 2: No indentar listas con 4 espacios

```html
❌ Incorrecto:
<pre>
👁️ <b>Items:</b>
- espada
- mochila
</pre>

✅ Correcto:
<pre>
👁️ <b>Items:</b>
    - espada
    - mochila
</pre>
```

### ❌ Error 3: Títulos en minúsculas

```html
❌ Incorrecto:
<pre>📦 <b>Tu Inventario</b></pre>

✅ Correcto:
<pre>📦 <b>TU INVENTARIO</b></pre>
```

### ❌ Error 4: Íconos hardcodeados

```python
# ❌ Incorrecto
message = f"<pre>🏛️ <b>{room.name}</b></pre>"

# ✅ Correcto
from src.templates import ICONS
message = f"<pre>{ICONS['room']} <b>{room.name.upper()}</b></pre>"
```

### ❌ Error 5: Olvidar los dos puntos en sub-secciones

```html
❌ Incorrecto:
<pre>🚪 <b>Salidas</b></pre>

✅ Correcto:
<pre>🚪 <b>Salidas:</b></pre>
```

---

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

6. **Listas pequeñas (< 20 items)**: Mostrar todo directamente

7. **Listas medianas (20-50 items)**: Usar límites con mensaje de truncado

8. **Listas grandes (> 50 items)**: Ofrecer comando dedicado con paginación

9. **Siempre**: Indicar al jugador cómo ver más items

---

## Resumen

1. **Outputs Descriptivos** = `<pre>` + títulos en MAYÚSCULAS + listas con 4 espacios
2. **Notificaciones Sociales** = `<i>` + sin íconos + tercera persona
3. **Notificaciones Privadas** = `<i>` + sin íconos + segunda persona
4. **Feedback** = texto plano + íconos de estado opcionales

**La regla de oro:** Si dudas sobre el formato, pregunta: *"¿Qué tipo de mensaje es?"* y sigue las reglas de esa categoría.

**La regla de plata:** SIEMPRE usa **4 espacios + guion** para listas en outputs descriptivos.

---

**Documentación Relacionada:**
- [Creando Comandos](creating-commands.md) - Guía completa de comandos
- [Filosofía del Proyecto](../getting-started/core-philosophy.md) - Motor vs Contenido
