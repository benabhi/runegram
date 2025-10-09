# Guía de Estilo de Outputs de Runegram

El objetivo de esta guía es asegurar que todos los mensajes que el jugador recibe sean claros, consistentes y estén optimizados para la lectura en dispositivos móviles a través de Telegram.

## Filosofía de Diseño

> **"Cada mensaje tiene un propósito específico y debe comunicarlo claramente."**

Runegram clasifica todos los outputs en **4 categorías principales**, cada una con su propio formato y propósito específico. Esta separación no es solo estilística, sino que refleja el **flujo de información** del juego.

---

## Las 4 Categorías de Outputs

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

## Ejemplos Completos por Categoría

### Output Descriptivo: `/mirar` (Sala)

```html
<pre>🏛️ <b>PLAZA CENTRAL DE RUNEGARD</b>
Estás en el corazón de la ciudad. Una gran fuente de mármol domina el centro.

👁️ <b>Cosas a la vista:</b>
    1. ⚔️ una espada oxidada
    2. 🎒 una mochila de cuero

👤 <b>Personajes:</b>
    - 👤 Gandalf
    - 👤 Aragorn

🚪 <b>Salidas:</b>
    - ⬆️ Norte (Calle de los Mercaderes)
    - ⬇️ Sur (El Templo Antiguo)</pre>
```

### Output Descriptivo: `/inventario`

```html
<pre>📦 <b>TU INVENTARIO</b>

    1. ⚔️ espada de hierro
    2. 🎒 mochila de cuero (3 items)
    3. 💎 gema brillante</pre>
```

### Output Descriptivo: `/quien`

```html
<pre>👤 <b>JUGADORES EN RUNEGRAM (3 conectados)</b>

    - Gandalf (🏛️ Plaza Central)
    - Aragorn (⚔️ Campo de Batalla) 💤 <i>AFK: comiendo</i>
    - Legolas (🌲 Bosque Verde)</pre>
```

### Notificación Social: Movimiento

```html
<i>Gandalf se ha ido hacia el norte.</i>
<i>Aragorn ha llegado desde el sur.</i>
```

### Notificación Social: Acción con Objeto

```html
<i>Frodo ha cogido una espada del suelo.</i>
<i>Sam ha dejado una mochila en el suelo.</i>
<i>Merry ha metido una poción en su mochila.</i>
```

### Notificación Privada: Susurro

```html
<i>Gandalf te susurra: "El enemigo se acerca."</i>
```

### Notificación Privada: Dar Objeto

```html
<i>Aragorn te da: una espada élfica.</i>
```

### Feedback Simple: Éxito

```html
Has cogido: una espada oxidada.
Dejas caer una mochila de cuero.
✅ Has activado el canal de Novatos.
```

### Feedback Simple: Error

```html
No ves ese objeto por aquí.
No ves a nadie con ese nombre por aquí.
❌ Ocurrió un error inesperado.
```

### Feedback Complejo: Desambiguación

```html
<pre>❓ Hay 2 'espada'. ¿Cuál quieres coger?

1. ⚔️ espada oxidada
2. ⚔️ espada brillante

Usa:
/coger 1.espada
/coger 2.espada</pre>
```

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

## Resumen

1. **Outputs Descriptivos** = `<pre>` + títulos en MAYÚSCULAS + listas con 4 espacios
2. **Notificaciones Sociales** = `<i>` + sin íconos + tercera persona
3. **Notificaciones Privadas** = `<i>` + sin íconos + segunda persona
4. **Feedback** = texto plano + íconos de estado opcionales

**La regla de oro:** Si dudas sobre el formato, pregunta: *"¿Qué tipo de mensaje es?"* y sigue las reglas de esa categoría.

---

**Versión:** 1.0
**Última actualización:** 2025-10-09
**Basado en:** `prompt.md` - Guía de estilo original del proyecto
