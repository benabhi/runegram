---
título: "Sistema de Narrativa"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["narrativa", "mensajes", "aleatorio", "inmersión"]
documentos_relacionados:
  - "engine-systems/broadcaster-service.md"
  - "content-creation/output-style-guide.md"
referencias_código:
  - "src/services/narrative_service.py"
  - "game_data/narrative_messages.py"
estado: "actual"
---

# Narrative System

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

## 📚 Tipos de Mensajes Disponibles

### 1. `item_spawn`
**Uso:** Cuando un admin genera un objeto con `/generarobjeto`

**Variables:**
- `{item_name}`: Nombre del objeto

**Comando que lo usa:** `/generarobjeto`

### 2. `item_destroy_room`
**Uso:** Cuando un objeto en una sala es destruido

**Variables:**
- `{item_name}`: Nombre del objeto

**Comando que lo usa:** `/destruirobjeto` (cuando el item está en una sala)

### 3. `item_destroy_inventory`
**Uso:** Cuando un objeto en un inventario de jugador es destruido

**Variables:**
- `{item_name}`: Nombre del objeto

**Comando que lo usa:** `/destruirobjeto` (cuando el item está en inventario)

### 4. `teleport_departure`
**Uso:** Cuando un admin se teletransporta - mensaje para la sala de origen

**Variables:**
- `{character_name}`: Nombre del personaje

**Comando que lo usa:** `/teleport` (broadcast a sala origen)

### 5. `teleport_arrival`
**Uso:** Cuando un admin llega por teletransporte - mensaje para la sala de destino

**Variables:**
- `{character_name}`: Nombre del personaje

**Comando que lo usa:** `/teleport` (broadcast a sala destino)

### 6. `character_suicide`
**Uso:** Cuando un jugador elimina su personaje con `/suicidio`

**Variables:**
- `{character_name}`: Nombre del personaje

**Comando que lo usa:** `/suicidio` (broadcast a sala actual)

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

## Ver También

- [Broadcaster Service](broadcaster-service.md) - Cómo se envían los mensajes a jugadores
- [Output Style Guide](../content-creation/output-style-guide.md) - Estándares de formato para mensajes
