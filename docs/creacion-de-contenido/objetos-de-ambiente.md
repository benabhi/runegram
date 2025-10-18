---
título: "Objetos de Ambiente (Fixtures)"
categoría: "Creación de Contenido"
audiencia: "creador-de-contenido"
última_actualización: "2025-10-18"
autor: "Proyecto Runegram"
etiquetas: ["fixtures", "ambiente", "objetos-fijos", "world-building", "decoración"]
documentos_relacionados:
  - "creacion-de-contenido/creacion-de-items.md"
  - "creacion-de-contenido/construccion-de-salas.md"
  - "sistemas-del-motor/sistema-de-prototipos.md"
  - "sistemas-del-motor/sistema-de-eventos.md"
referencias_código:
  - "game_data/item_prototypes.py"
  - "game_data/room_prototypes.py"
  - "src/services/world_loader_service.py"
  - "src/templates/base/room.html.j2"
estado: "actual"
importancia: "alta"
---

# Objetos de Ambiente (Fixtures)

Los **fixtures** son objetos que forman parte integral del ambiente de una sala. A diferencia de los items regulares, los fixtures están diseñados para ser elementos permanentes del entorno que enriquecen la atmósfera y la interactividad del mundo sin poder ser movidos fácilmente.

## ¿Qué es un Fixture?

Un fixture es un objeto especial que:

- ✅ Forma parte del ambiente permanente de una sala
- ✅ Es completamente interactuable (mirar, usar, scripts)
- ✅ Está fijo en su ubicación (no se puede coger normalmente)
- ✅ Se muestra integrado en la descripción de la sala
- ✅ Se sincroniza automáticamente al iniciar el bot
- ✅ Puede tener scripts reactivos y proactivos
- ✅ Puede tener estado persistente y transiente

## Fixtures vs. Detalles vs. Items Regulares

Es importante entender las diferencias entre estos tres tipos de elementos:

| Característica | Fixtures | Detalles | Items Regulares |
|---------------|----------|----------|-----------------|
| **Objeto físico** | ✅ Sí (Item completo) | ❌ Solo texto | ✅ Sí (Item completo) |
| **Se puede mirar** | ✅ Sí | ✅ Sí | ✅ Sí |
| **Se puede coger** | ❌ No (bloqueado) | ❌ No existe | ✅ Sí |
| **Se puede usar** | ✅ Sí | ❌ No | ✅ Sí |
| **Scripts reactivos** | ✅ Sí | ❌ No | ✅ Sí |
| **Scripts proactivos** | ✅ Sí | ❌ No | ✅ Sí |
| **Estado persistente** | ✅ Sí | ❌ No | ✅ Sí |
| **En descripción** | ✅ Integrado | ➖ N/A | ❌ En "Cosas a la vista" |
| **Sincronización** | ✅ Automática | ➖ N/A | ❌ Manual |

### Cuándo Usar Cada Tipo

**Usa Fixtures cuando:**
- El elemento es parte permanente del ambiente (fuente, árbol, estatua)
- Necesitas interactividad completa (scripts, estado, uso)
- Quieres que aparezca integrado en la descripción de la sala
- El objeto debe persistir entre reinicios automáticamente

**Usa Detalles cuando:**
- Solo necesitas texto descriptivo (sin scripts ni estado)
- El elemento es puramente visual (pintura, inscripción)
- No requieres ningún tipo de interacción más allá de mirar

**Usa Items Regulares cuando:**
- El objeto puede ser recogido y transportado
- Su ubicación cambia dinámicamente
- Es parte del inventario del jugador

## Creando un Fixture

### Paso 1: Definir el Prototipo en `item_prototypes.py`

Los fixtures se definen exactamente igual que items regulares, pero con el flag especial `is_fixture: True` y locks contextuales que previenen que sean recogidos:

```python
# En game_data/item_prototypes.py

"fuente_magica_plaza": {
    "name": "una fuente mágica",
    "keywords": ["fuente", "magica", "fuente magica", "marmol"],
    "description": "Una magnífica fuente de mármol blanco con aguas cristalinas que brillan con un tenue resplandor azulado. Las runas grabadas en su base emiten un leve zumbido mágico.",
    "category": "ambiente",
    "tags": ["fuente", "magica", "fija"],

    # Flag crítico: marca este objeto como fixture
    "is_fixture": True,

    # Locks contextuales: solo SUPERADMIN puede cogerlo
    "locks": {
        "get": "rol(SUPERADMIN)"
    },

    # Mensajes personalizados (opcional)
    "lock_messages": {
        "get": "La fuente es parte integral de la plaza. No puedes llevártela."
    },

    # Scripts reactivos (opcional)
    "scripts": {
        "after_on_look": """
await context.send_message(character, '<i>Las aguas de la fuente brillan intensamente al sentir tu mirada.</i>')
"""
    },

    "display": {
        "icon": "⛲",
    }
}
```

**Campos Críticos:**
- `is_fixture: True` - Marca el objeto como fixture
- `locks: {"get": "rol(SUPERADMIN)"}` - Previene que sea recogido
- `lock_messages` - Mensajes personalizados al intentar recogerlo

### Paso 2: Agregar el Fixture a una Sala

Una vez definido el prototipo, agrégalo al campo `fixtures` de la sala en `room_prototypes.py`:

```python
# En game_data/room_prototypes.py

"plaza_central": {
    "name": "Plaza Central de Runegard",
    "description": "Estás en el corazón de la ciudad. El bullicio de mercaderes y aventureros llena el aire.",
    "category": "ciudad_runegard",
    "tags": ["ciudad", "seguro", "social", "exterior"],

    # Lista de fixtures (keys de item_prototypes.py)
    "fixtures": [
        "fuente_magica_plaza",
        "arbol_frutal_plaza",
        "estatua_guerrero"
    ],

    "exits": {
        "sur": "limbo",
        "este": "calle_mercaderes"
    },

    "display": {
        "icon": "🏛️",
    }
}
```

### Paso 3: Reiniciar el Bot

Los fixtures se sincronizan automáticamente al iniciar el bot:

```bash
docker-compose restart
```

El `world_loader_service` ejecutará:
1. Lectura del campo `fixtures` de cada sala
2. Verificación de existencia (no duplica fixtures en reinicios)
3. Creación de fixtures nuevos preservando `script_state`
4. Log de operaciones realizadas

**El proceso es idempotente**: reiniciar el bot múltiples veces no duplicará fixtures.

## Ejemplos de Fixtures

### Fuente Mágica Decorativa

Una fuente que reacciona cuando la miran:

```python
"fuente_magica_plaza": {
    "name": "una fuente mágica",
    "keywords": ["fuente", "magica", "fuente magica", "marmol"],
    "description": "Una magnífica fuente de mármol blanco con aguas cristalinas que brillan con un tenue resplandor azulado.",
    "category": "ambiente",
    "tags": ["fuente", "magica", "fija"],
    "is_fixture": True,
    "locks": {
        "get": "rol(SUPERADMIN)"
    },
    "lock_messages": {
        "get": "La fuente es parte integral de la plaza. No puedes llevártela."
    },
    "scripts": {
        "after_on_look": """
await context.send_message(character, '<i>Las aguas de la fuente brillan intensamente al sentir tu mirada.</i>')
"""
    },
    "display": {
        "icon": "⛲",
    }
}
```

**Resultado**: Al usar `/mirar fuente`, el jugador ve la descripción Y recibe un mensaje especial sobre el brillo.

### Árbol Frutal con Generación Periódica

Un árbol que produce manzanas cada 6 horas:

```python
"arbol_frutal_plaza": {
    "name": "un árbol frutal",
    "keywords": ["arbol", "frutal", "arbol frutal", "manzano"],
    "description": "Un hermoso manzano de ramas retorcidas y hojas verdes vibrantes. Entre las hojas se asoman algunas manzanas rojas maduras.",
    "category": "ambiente",
    "tags": ["arbol", "frutal", "fijo"],
    "is_fixture": True,
    "locks": {
        "get": "rol(SUPERADMIN)"
    },
    "lock_messages": {
        "get": "El árbol tiene raíces profundas. No puedes arrancarlo del suelo."
    },
    "scheduled_scripts": [
        {
            "schedule": "0 */6 * * *",  # Cada 6 horas (sintaxis cron)
            "script": "global:spawn_item(item_key='manzana_roja', mensaje='Una manzana madura cae del árbol con un suave golpe')",
            "permanent": True,
            "global": True,
            "category": "ambient"
        }
    ],
    "display": {
        "icon": "🌳",
    }
}

# Item que genera el árbol
"manzana_roja": {
    "name": "una manzana roja",
    "keywords": ["manzana", "roja", "fruta"],
    "description": "Una manzana roja brillante, jugosa y apetitosa.",
    "category": "consumible",
    "tags": ["fruta", "consumible"],
    "scripts": {
        "after_on_use": "global:curar_personaje(cantidad=10, mensaje='La manzana te restaura un poco de energía')"
    },
    "display": {
        "icon": "🍎",
    }
}
```

**Resultado**: Cada 6 horas, aparece automáticamente una manzana en la sala. Los jugadores pueden coger y comer las manzanas.

### Palanca con Estado Persistente

Una palanca que solo se puede activar una vez:

```python
"palanca_secreta": {
    "name": "una palanca de hierro",
    "keywords": ["palanca", "hierro", "manija"],
    "description": "Una palanca de hierro oxidado sobresale de la pared. Parece activar algún mecanismo.",
    "category": "mecanismo",
    "tags": ["palanca", "mecanismo", "fijo"],
    "is_fixture": True,
    "locks": {
        "get": "rol(SUPERADMIN)",
        "use": ""  # Todos pueden usarla
    },
    "lock_messages": {
        "get": "La palanca está firmemente fijada a la pared."
    },
    "scripts": {
        "after_on_use": """
from src.services import state_service

# Verificar si ya fue activada
activada = await state_service.get_persistent(session, target, 'activada', default=False)

if not activada:
    await state_service.set_persistent(session, target, 'activada', True)
    await context.send_message(character, '✅ ¡La palanca se mueve con un clic! Escuchas el sonido de piedra moviéndose en la distancia.')
    # Aquí podrías agregar lógica para abrir una salida, etc.
else:
    await context.send_message(character, '⚠️ La palanca ya ha sido activada. No sucede nada.')
"""
    },
    "display": {
        "icon": "🎚️",
    }
}
```

**Resultado**: La primera vez que alguien usa `/usar palanca`, se activa. Intentos posteriores no hacen nada.

### Estatua con Mensajes Aleatorios y Cooldown

Una estatua que muestra mensajes aleatorios evitando spam:

```python
"estatua_guerrero": {
    "name": "una estatua de guerrero",
    "keywords": ["estatua", "guerrero", "escultura"],
    "description": "Una imponente estatua de piedra que representa a un guerrero antiguo con armadura completa. Sus ojos de gema parecen seguirte mientras te mueves.",
    "category": "ambiente",
    "tags": ["estatua", "decoracion", "fijo"],
    "is_fixture": True,
    "locks": {
        "get": "rol(SUPERADMIN)"
    },
    "lock_messages": {
        "get": "La estatua es maciza y está anclada al pedestal. Pesa toneladas."
    },
    "scripts": {
        "after_on_look": """
import random
from src.services import state_service

# Verificar cooldown (evitar spam)
if await state_service.is_on_cooldown(target, 'mensaje_estatua'):
    return

# Mensajes aleatorios
mensajes = [
    '<i>Los ojos de gema de la estatua brillan fugazmente.</i>',
    '<i>La estatua parece vigilante, como si protegiera algo.</i>',
    '<i>Sientes una presencia antigua emanando de la piedra.</i>',
]

mensaje = random.choice(mensajes)
await context.send_message(character, mensaje)

# Establecer cooldown de 30 segundos
from datetime import timedelta
await state_service.set_cooldown(target, 'mensaje_estatua', timedelta(seconds=30))
"""
    },
    "display": {
        "icon": "🗿",
    }
}
```

**Resultado**: Cada vez que alguien mira la estatua (máximo 1 vez cada 30s), recibe un mensaje aleatorio.

## Presentación Visual en el Juego

Los fixtures se muestran de manera especial en la descripción de la sala:

```
🏛️ PLAZA CENTRAL DE RUNEGARD
Estás en el corazón de la ciudad. El bullicio de mercaderes y aventureros llena el aire.
⛲ Una fuente mágica.
🌳 Un árbol frutal.
🗿 Una estatua de guerrero.

👁️ Cosas a la vista:
    1. ⚔️ una espada oxidada
    2. 🧪 una poción de vida

🚶 Personajes:
    - 🧙 Gandalf
    - ⚔️ Aragorn

🚪 Salidas:
    - ⬆️ Norte (Calle de los Mercaderes)
    - ⬇️ Sur (El Limbo)
```

**Nota**: Los fixtures aparecen integrados en la descripción de la sala (sin numeración), mientras que los items regulares aparecen en "Cosas a la vista" (con numeración).

## Interacción con Fixtures

Los jugadores pueden interactuar con fixtures usando los mismos comandos que con items regulares:

```bash
# Mirar fixture
/mirar fuente
→ Muestra descripción + scripts de on_look

# Usar fixture (si tiene scripts de on_use)
/usar palanca
→ Ejecuta lógica del script

# Intentar coger fixture
/coger fuente
→ "La fuente es parte integral de la plaza. No puedes llevártela."
```

## Sincronización Automática

Los fixtures tienen una ventaja importante: **sincronización automática** al iniciar el bot.

### ¿Cómo Funciona?

El `world_loader_service` ejecuta `_sync_room_fixtures()` como **PASO 4** en `sync_world_from_prototypes()`:

1. Lee el campo `fixtures` de cada sala en `ROOM_PROTOTYPES`
2. Para cada fixture definido:
   - Verifica si ya existe en la sala (por `key` y `room_id`)
   - Si NO existe: lo crea
   - Si YA existe: lo mantiene (preserva `script_state`)
3. Registra todas las operaciones en el log

**Ventajas**:
- ✅ Idempotente (no duplica fixtures en reinicios)
- ✅ Preserva estado persistente (`script_state`)
- ✅ Automático (no requiere comandos de admin)
- ✅ Seguro (solo crea, nunca borra)

### Código Relevante

```python
# En src/services/world_loader_service.py

async def _sync_room_fixtures(session: AsyncSession, room_key_to_id_map: dict):
    """
    Sincroniza los fixtures (objetos de ambiente) definidos en las salas.

    Esta función es idempotente: no duplicará fixtures en reinicios.
    """
    logging.info("  -> Sincronizando fixtures de salas...")

    for room_key, room_data in ROOM_PROTOTYPES.items():
        fixture_keys = room_data.get("fixtures", [])
        if not fixture_keys:
            continue

        room_id = room_key_to_id_map.get(room_key)
        if not room_id:
            logging.warning(f"  -> Sala '{room_key}' no encontrada en mapa de IDs. Ignorando fixtures.")
            continue

        for item_key in fixture_keys:
            # Verificar que el prototipo existe
            if item_key not in ITEM_PROTOTYPES:
                logging.warning(f"  -> Fixture '{item_key}' no existe en ITEM_PROTOTYPES. Ignorando.")
                continue

            # Verificar si el fixture ya existe en esta sala
            result = await session.execute(
                select(Item).where(Item.key == item_key, Item.room_id == room_id)
            )
            existing_fixture = result.scalar_one_or_none()

            if existing_fixture:
                # Ya existe, mantenerlo (preserva script_state)
                logging.debug(f"  -> Fixture '{item_key}' ya existe en '{room_key}'. Manteniendo.")
            else:
                # Crear nuevo fixture
                new_fixture = Item(key=item_key, room_id=room_id)
                session.add(new_fixture)
                logging.info(f"  -> Creado fixture '{item_key}' en '{room_key}'.")
```

## Mejores Prácticas

### 1. Nomenclatura de Keys

Usa un sufijo que identifique la sala para evitar conflictos:

```python
# ✅ Bueno: Identificable por sala
"fuente_magica_plaza"
"arbol_frutal_bosque"
"estatua_templo"

# ❌ Malo: Nombres genéricos
"fuente"
"arbol"
"estatua"
```

### 2. Keywords Descriptivos

Incluye múltiples formas de referirse al fixture:

```python
"keywords": ["fuente", "magica", "fuente magica", "marmol", "agua"]
```

**Permite**: `/mirar fuente`, `/mirar fuente magica`, `/mirar agua`

### 3. Mensajes de Lock Personalizados

Siempre proporciona mensajes contextuales al intentar recoger:

```python
# ✅ Bueno: Mensaje contextual
"lock_messages": {
    "get": "El árbol tiene raíces profundas. No puedes arrancarlo del suelo."
}

# ❌ Malo: Mensaje genérico (default)
# "No puedes hacer eso."
```

### 4. Scripts con Cooldowns

Para fixtures interactivos, usa cooldowns para evitar spam:

```python
# Verificar cooldown antes de ejecutar
if await state_service.is_on_cooldown(target, 'accion_especial'):
    return

# ... ejecutar lógica ...

# Establecer cooldown
from datetime import timedelta
await state_service.set_cooldown(target, 'accion_especial', timedelta(seconds=30))
```

### 5. Categorías y Tags Apropiadas

Usa categoría `"ambiente"` y tags descriptivos:

```python
"category": "ambiente",
"tags": ["fuente", "magica", "fija", "decoracion"]
```

### 6. Íconos Descriptivos

Usa emojis que representen visualmente el fixture:

```python
"display": {
    "icon": "⛲"  # Fuente
}
```

**Íconos comunes para fixtures**:
- Fuentes: ⛲
- Árboles: 🌳 🌲 🎄
- Estatuas: 🗿 🗽
- Mobiliario: 🪑 🛋️ 🛏️
- Iluminación: 🕯️ 🔥 💡
- Plantas: 🌺 🌻 🌹
- Arquitectura: 🏛️ ⛩️ 🏰

## Solución de Problemas

### "El fixture no aparece en la sala"

**Posibles causas**:
1. La `key` del fixture no está en `ITEM_PROTOTYPES`
   - Verifica que el prototipo existe
2. La `key` del fixture no está en el campo `fixtures` de la sala
   - Revisa `room_prototypes.py`
3. No reiniciaste el bot
   - Ejecuta `docker-compose restart`

**Verificación**:
```bash
# Ver logs del bot
docker logs runegram-bot-1 | grep -i "fixture"
```

### "Puedo coger el fixture"

**Causa**: Falta el lock contextual `"get": "rol(SUPERADMIN)"`

**Solución**:
```python
"locks": {
    "get": "rol(SUPERADMIN)"  # Agregar este lock
}
```

### "El fixture se duplica en cada reinicio"

**Causa**: Esto NO debería pasar si `_sync_room_fixtures()` funciona correctamente.

**Verificación**:
1. Revisa logs: `docker logs runegram-bot-1 | grep -i "fixture"`
2. Verifica que `world_loader_service` está ejecutando PASO 4
3. Reporta el bug si persiste

**Workaround temporal** (como admin):
```bash
/destruirobjeto fuente_duplicada
```

### "El script del fixture no se ejecuta"

**Posibles causas**:
1. Sintaxis incorrecta del script
2. Script no registrado en `script_service`
3. Error en la ejecución

**Solución**:
```bash
# Ver logs de errores de scripts
docker logs runegram-bot-1 | grep -i "error"
```

### "El estado persistente del fixture se pierde"

**Causa**: Esto NO debería pasar. `_sync_room_fixtures()` preserva `script_state`.

**Verificación**:
1. Confirma que el fixture YA existía antes del reinicio
2. Revisa logs de sincronización
3. Verifica que el estado se guardó con `await session.commit()`

## Resumen

Los fixtures son objetos de ambiente que enriquecen el mundo del juego:

1. **Define el prototipo** en `item_prototypes.py` con `is_fixture: True`
2. **Agrega locks contextuales** para prevenir que sean recogidos
3. **Incluye en la sala** agregando la `key` al campo `fixtures` en `room_prototypes.py`
4. **Reinicia el bot** para sincronizar automáticamente
5. **Aprovecha scripts** para crear fixtures interactivos y dinámicos

**Ventajas clave**:
- Sincronización automática (idempotente)
- Presentación integrada en descripción de sala
- Interactividad completa (scripts, estado, uso)
- Persistencia entre reinicios

¡Los fixtures transforman salas estáticas en entornos vivos y memorables!

---

**Documentación Relacionada:**
- [Creando Items](creacion-de-items.md) - Prototipos de items
- [Construyendo Salas](construccion-de-salas.md) - Prototipos de salas
- [Sistema de Prototipos](../sistemas-del-motor/sistema-de-prototipos.md) - Arquitectura
- [Sistema de Eventos](../sistemas-del-motor/sistema-de-eventos.md) - Scripts reactivos
- [Sistema de Scheduling](../sistemas-del-motor/sistema-de-scheduling.md) - Scripts proactivos
- [Sistema de Estado](../sistemas-del-motor/sistema-de-estado.md) - Estado persistente/transiente
