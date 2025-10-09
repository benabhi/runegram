# Sistema de Narrativa (Narrative Service)

## 🎯 Visión General

El **Narrative Service** es un sistema centralizado que proporciona mensajes narrativos evocativos y aleatorios para diversos eventos del juego, mejorando significativamente la inmersión y evitando la repetición de texto que haría que el mundo se sienta estático y predecible.

## 🎨 Filosofía de Diseño

### Problema que Resuelve

En los MUDs tradicionales, los mensajes de eventos suelen ser estáticos y repetitivos:

❌ **Sin Narrative Service:**
```
> generar espada
✅ Objeto 'Espada Brillante' generado.
Una espada brillante aparece de la nada.

> generar espada
✅ Objeto 'Espada Brillante' generado.
Una espada brillante aparece de la nada.  ← Siempre el mismo mensaje
```

✅ **Con Narrative Service:**
```
> generar espada
✅ Objeto 'Espada Brillante' generado.
Una espada brillante se materializa con un destello de luz.

> generar espada
✅ Objeto 'Espada Brillante' generado.
Un portal dimensional deposita una espada brillante en el suelo.  ← Variedad!
```

### Principios Fundamentales

1. **Variedad**: Cada tipo de evento tiene 5-7 variantes de mensajes equivalentes
2. **Inmersión**: Los mensajes son evocativos y apropiados para el género de fantasía
3. **Centralización**: Todos los mensajes narrativos en un solo lugar (`game_data/narrative_messages.py`)
4. **Escalabilidad**: Agregar nuevos tipos de mensajes es trivial
5. **Consistencia**: API uniforme para todos los comandos

---

## 📁 Arquitectura

### Componentes

```
game_data/
  └── narrative_messages.py    # Base de datos de mensajes (contenido)

src/services/
  └── narrative_service.py     # API para obtener mensajes (motor)

commands/
  ├── admin/
  │   ├── building.py          # Usa: item_spawn, item_destroy_*
  │   └── movement.py          # Usa: teleport_departure, teleport_arrival
  └── player/
      └── character.py         # Usa: character_suicide
```

### Separación Motor/Contenido

El sistema respeta estrictamente la filosofía de separación:

- **Motor** (`narrative_service.py`): Lógica genérica en inglés para obtener mensajes aleatorios
- **Contenido** (`narrative_messages.py`): Mensajes específicos del juego en español

---

## 🔧 API del Narrative Service

### Función Principal: `get_random_narrative()`

```python
from src.services import narrative_service

message = narrative_service.get_random_narrative(
    message_type="item_spawn",
    item_name="una espada brillante"
)
# Resultado (aleatorio): "<i>Una espada brillante se materializa con un destello.</i>"
```

**Parámetros:**
- `message_type` (str): Tipo de mensaje (debe existir en `NARRATIVE_MESSAGES`)
- `**kwargs`: Variables para formatear el mensaje (ej: `item_name`, `character_name`)

**Retorna:**
- `str`: Mensaje formateado con las variables proporcionadas

**Excepciones:**
- `ValueError`: Si el `message_type` no existe

### Funciones Auxiliares

#### `get_available_message_types()`
```python
types = narrative_service.get_available_message_types()
# Retorna: ['item_spawn', 'item_destroy_room', 'teleport_departure', ...]
```

#### `get_message_count(message_type)`
```python
count = narrative_service.get_message_count("item_spawn")
# Retorna: 7 (número de variantes disponibles)
```

---

## 📚 Tipos de Mensajes Disponibles

### 1. `item_spawn`
**Uso:** Cuando un admin genera un objeto con `/generarobjeto`

**Variables:**
- `{item_name}`: Nombre del objeto

**Ejemplo:**
```python
message = narrative_service.get_random_narrative(
    "item_spawn",
    item_name="una poción roja"
)
# Resultado: "<i>Una poción roja aparece de la nada.</i>"
```

**Comando que lo usa:** `/generarobjeto`

---

### 2. `item_destroy_room`
**Uso:** Cuando un objeto en una sala es destruido

**Variables:**
- `{item_name}`: Nombre del objeto

**Ejemplo:**
```python
message = narrative_service.get_random_narrative(
    "item_destroy_room",
    item_name="una espada"
)
# Resultado: "<i>Una espada se desvanece en el aire.</i>"
```

**Comando que lo usa:** `/destruirobjeto` (cuando el item está en una sala)

---

### 3. `item_destroy_inventory`
**Uso:** Cuando un objeto en un inventario de jugador es destruido

**Variables:**
- `{item_name}`: Nombre del objeto

**Ejemplo:**
```python
message = narrative_service.get_random_narrative(
    "item_destroy_inventory",
    item_name="una espada"
)
# Resultado: "Sientes cómo una espada desaparece de tu inventario."
```

**Comando que lo usa:** `/destruirobjeto` (cuando el item está en inventario)

---

### 4. `teleport_departure`
**Uso:** Cuando un admin se teletransporta - mensaje para la sala de origen

**Variables:**
- `{character_name}`: Nombre del personaje

**Ejemplo:**
```python
message = narrative_service.get_random_narrative(
    "teleport_departure",
    character_name="Gandalf"
)
# Resultado: "<i>Gandalf desaparece en un destello brillante.</i>"
```

**Comando que lo usa:** `/teleport` (broadcast a sala origen)

---

### 5. `teleport_arrival`
**Uso:** Cuando un admin llega por teletransporte - mensaje para la sala de destino

**Variables:**
- `{character_name}`: Nombre del personaje

**Ejemplo:**
```python
message = narrative_service.get_random_narrative(
    "teleport_arrival",
    character_name="Gandalf"
)
# Resultado: "<i>Gandalf aparece de la nada.</i>"
```

**Comando que lo usa:** `/teleport` (broadcast a sala destino)

---

### 6. `character_suicide`
**Uso:** Cuando un jugador elimina su personaje con `/suicidio`

**Variables:**
- `{character_name}`: Nombre del personaje

**Ejemplo:**
```python
message = narrative_service.get_random_narrative(
    "character_suicide",
    character_name="Frodo"
)
# Resultado: "<i>Frodo desaparece en una luz cegadora.</i>"
```

**Comando que lo usa:** `/suicidio` (broadcast a sala actual)

---

## 🛠️ Implementación en Comandos

### Patrón Estándar

```python
from src.services import narrative_service, broadcaster_service

# 1. Obtener mensaje narrativo aleatorio
narrative_message = narrative_service.get_random_narrative(
    "item_spawn",
    item_name=item_name
)

# 2. Enviar a los jugadores (broadcast filtra automáticamente offline)
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=room_id,
    message_text=narrative_message,
    exclude_character_id=None  # O el ID del ejecutor si no quieres que lo vea
)
```

### Ejemplo Completo: `/generarobjeto`

```python
# Mensaje al admin (estático, confirmación técnica)
await message.answer(f"✅ Objeto '{item_name}' generado en la sala actual.")

# Mensaje social a la sala (narrativo, aleatorio)
narrative_message = narrative_service.get_random_narrative(
    "item_spawn",
    item_name=item_name
)
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=character.room_id,
    message_text=narrative_message,
    exclude_character_id=None
)
```

**Resultado para jugadores en la sala:**
- Admin ve: `✅ Objeto 'Espada Brillante' generado en la sala actual.`
- Otros ven (aleatorio):
  - `Espada brillante aparece de la nada.`
  - `Espada brillante se materializa con un destello de luz.`
  - `Un portal dimensional deposita espada brillante en el suelo.`
  - ... etc.

---

## 📝 Agregar Nuevos Tipos de Mensajes

### Paso 1: Definir mensajes en `narrative_messages.py`

```python
# game_data/narrative_messages.py

NARRATIVE_MESSAGES = {
    # ... mensajes existentes ...

    "new_event_type": [
        "<i>{variable_name} hace algo evocativo.</i>",
        "<i>{variable_name} hace algo diferente pero equivalente.</i>",
        "<i>{variable_name} hace una tercera cosa interesante.</i>",
        # ... agregar 4-7 variantes
    ],
}
```

**Buenas Prácticas:**
- Crear al menos 5 variantes para variedad genuina
- Mantener tono consistente con el género del juego (fantasía medieval)
- Usar `<i>` para mensajes sociales (tercera persona)
- Usar texto plano para mensajes privados (segunda persona)
- Nombrar variables de forma descriptiva (`{item_name}`, `{character_name}`, no `{x}`)

### Paso 2: Usar en un comando

```python
from src.services import narrative_service

message = narrative_service.get_random_narrative(
    "new_event_type",
    variable_name="valor"
)
```

---

## 🎯 Casos de Uso Actuales

### `/generarobjeto` - Aparición de Objetos
**Tipo:** `item_spawn`
**Comportamiento:** Todos los jugadores online en la sala ven un mensaje aleatorio

### `/destruirobjeto` - Destrucción de Objetos
**Tipos:**
- `item_destroy_room` (item en sala)
- `item_destroy_inventory` (item en inventario)

**Comportamiento:**
- Si está en **sala**: Broadcast a jugadores online
- Si está en **inventario**: Mensaje privado al dueño + broadcast a sala donde está
- Si está en **contenedor**: Solo mensaje al admin (sin broadcast)

### `/teleport` - Teletransporte de Admin
**Tipos:**
- `teleport_departure` (sala origen)
- `teleport_arrival` (sala destino)

**Comportamiento:**
- Broadcast a sala origen (salida) - excluye al admin
- Broadcast a sala destino (llegada) - excluye al admin
- Admin ve mensaje técnico simple

### `/suicidio` - Eliminación de Personaje
**Tipo:** `character_suicide`

**Comportamiento:**
- Broadcast a sala actual antes de eliminar el personaje
- Excluye al suicida (no ve su propia desaparición)

---

## 🔮 Futuras Extensiones

### Mensajes Contextuales
```python
# Mensaje diferente según el clima de la sala
if room.weather == "rain":
    message_type = "item_spawn_rain"
else:
    message_type = "item_spawn"
```

### Mensajes por Prototipo
```python
# Permitir que prototipos definan sus propios mensajes
ITEM_PROTOTYPES = {
    "espada_viviente": {
        "name": "Espada Viviente",
        "narrative_messages": {
            "spawn": [
                "<i>La espada viviente corta el tejido de la realidad para emerger.</i>",
                # ... mensajes únicos para este item
            ]
        }
    }
}
```

### Migración a TOML
Si se desea mayor configurabilidad sin modificar código Python:

```toml
# gameconfig.toml o narrative_messages.toml

[narrative.item_spawn]
messages = [
    "<i>{item_name} aparece de la nada.</i>",
    "<i>{item_name} se materializa con un destello de luz.</i>",
]
```

---

## 📊 Estadísticas Actuales

| Tipo de Mensaje | Variantes | Comandos que lo Usan |
|-----------------|-----------|----------------------|
| `item_spawn` | 7 | `/generarobjeto` |
| `item_destroy_room` | 7 | `/destruirobjeto` |
| `item_destroy_inventory` | 6 | `/destruirobjeto` |
| `teleport_departure` | 7 | `/teleport` |
| `teleport_arrival` | 7 | `/teleport` |
| `character_suicide` | 7 | `/suicidio` |

**Total:** 41 variantes de mensajes narrativos

---

## 🧪 Testing

### Verificar Variedad
Ejecutar el mismo comando varias veces y confirmar que los mensajes varían:

```bash
/generarobjeto espada
/generarobjeto espada
/generarobjeto espada
# Los mensajes deberían ser diferentes (probabilísticamente)
```

### Verificar Formateo
Confirmar que las variables se reemplazan correctamente:

```python
message = narrative_service.get_random_narrative(
    "item_spawn",
    item_name="Test Item 123"
)
# Verificar que "Test Item 123" aparece en el mensaje
```

---

## 📖 Ver También

- **[Sistema de Broadcasting](./04_BROADCASTER_SERVICE.md)** - Cómo se envían los mensajes a jugadores
- **[Guía de Admin](../05_ADMIN_GUIDE.md)** - Comandos que usan el narrative service
- **[Output Style Guide](../04_CONTENT_CREATION/05_OUTPUT_STYLE_GUIDE.md)** - Estándares de formato para mensajes

---

**Versión:** 1.0
**Última actualización:** 2025-01-09
**Autor:** Sistema Runegram
