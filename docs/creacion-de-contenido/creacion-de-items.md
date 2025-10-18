---
título: "Creando Items en Runegram"
categoría: "Creación de Contenido"
audiencia: "creador-de-contenido"
última_actualización: "2025-10-18"
autor: "Proyecto Runegram"
etiquetas: ["items", "prototipos", "contenedores", "locks", "locks-contextuales", "objetos", "eventos", "scripts", "fixtures"]
documentos_relacionados:
  - "creacion-de-contenido/objetos-de-ambiente.md"
  - "sistemas-del-motor/sistema-de-prototipos.md"
  - "creacion-de-contenido/construccion-de-salas.md"
  - "creacion-de-contenido/escritura-de-scripts.md"
  - "sistemas-del-motor/sistema-de-permisos.md"
referencias_código:
  - "game_data/item_prototypes.py"
  - "commands/player/interaction.py"
estado: "actual"
importancia: "alta"
---

# Creando Items en Runegram

Esta guía te muestra cómo crear objetos (items) en Runegram editando archivos de prototipos. Los items pueden ser simples objetos decorativos, armas funcionales, contenedores, o incluso objetos mágicos con comportamientos reactivos.

## Archivo a Editar: `game_data/item_prototypes.py`

Todas las definiciones de items viven en el diccionario `ITEM_PROTOTYPES` en este archivo. Los items se crean en el juego usando el comando de admin `/generarobjeto <key>`.

## Estructura de un Prototipo de Item

```python
"unique_key": {
    "name": str,                      # Nombre del objeto mostrado a los jugadores
    "keywords": list[str],            # Palabras clave para identificar el objeto
    "description": str,                # Descripción mostrada al examinar
    "category": str,                   # Opcional: Categoría principal
    "tags": list[str],                # Opcional: Etiquetas múltiples
    "locks": str,                      # Opcional: Lock para coger el objeto
    "is_container": bool,              # Opcional: ¿Es un contenedor?
    "capacity": int,                   # Opcional: Capacidad si es contenedor
    "grants_command_sets": list[str],  # Opcional: Comandos otorgados al equipar
    "attributes": dict,                # Opcional: Atributos personalizados
    "scripts": dict,                   # Opcional: Scripts reactivos (on_look, etc.)
    "tick_scripts": list[dict],        # Opcional: Scripts proactivos (scheduling)
    "display": {
        "icon": str,                   # Opcional: Emoji personalizado
        "template": str                # Opcional: Template Jinja2 personalizado
    }
}
```

---

## Creando un Item Básico

Vamos a crear una espada simple:

```python
# En game_data/item_prototypes.py

ITEM_PROTOTYPES = {
    # ... items existentes ...

    "espada_hierro": {
        "name": "una espada de hierro",
        "keywords": ["espada", "hierro", "espada de hierro"],
        "description": "Una espada básica de hierro forjada de manera competente. La hoja tiene algunas muescas pero está afilada.",
        "category": "arma",
        "tags": ["arma", "espada", "hierro", "común"],
        "display": {
            "icon": "⚔️"
        }
    }
}
```

**Para crear este objeto en el juego** (como admin):
```
/generarobjeto espada_hierro
```

El objeto aparecerá en tu inventario.

---

## Items de Ambiente (Fixtures)

Los **fixtures** son objetos especiales que forman parte permanente del ambiente de una sala. Son items completos con scripts y estado, pero están diseñados para permanecer fijos en su ubicación.

### Características de los Fixtures

- ✅ Se sincronizan automáticamente al iniciar el bot
- ✅ Se muestran integrados en la descripción de la sala
- ✅ No se pueden coger normalmente (bloqueados)
- ✅ Completamente interactuables (mirar, usar, scripts)
- ✅ Pueden tener estado persistente y transiente

### Creando un Fixture

Para crear un fixture, usa el flag `is_fixture: True` y locks contextuales:

```python
"fuente_magica_plaza": {
    "name": "una fuente mágica",
    "keywords": ["fuente", "magica", "fuente magica"],
    "description": "Una magnífica fuente de mármol blanco con aguas cristalinas que brillan.",
    "category": "ambiente",
    "tags": ["fuente", "magica", "fija"],

    # Flag crítico: marca como fixture
    "is_fixture": True,

    # Previene que sea recogido
    "locks": {
        "get": "rol(SUPERADMIN)"
    },
    "lock_messages": {
        "get": "La fuente es parte integral de la plaza. No puedes llevártela."
    },

    # Scripts reactivos (opcional)
    "scripts": {
        "after_on_look": """
await context.send_message(character, '<i>Las aguas brillan al sentir tu mirada.</i>')
"""
    },

    "display": {
        "icon": "⛲"
    }
}
```

### Agregando Fixtures a Salas

Una vez definido, agrégalo al campo `fixtures` de la sala:

```python
# En game_data/room_prototypes.py

"plaza_central": {
    "name": "Plaza Central de Runegard",
    "description": "Estás en el corazón de la ciudad...",
    "fixtures": [
        "fuente_magica_plaza",
        "arbol_frutal_plaza"
    ],
    # ... resto de la configuración ...
}
```

**Sincronización**: Los fixtures se crean automáticamente al iniciar el bot. No requieren comandos de admin.

**Ver**: [Objetos de Ambiente](objetos-de-ambiente.md) para documentación completa sobre fixtures.

---

## Items con Atributos

Los atributos permiten agregar propiedades personalizadas a los items que pueden ser usadas por sistemas futuros (combate, crafting, etc.):

```python
"espada_fuego": {
    "name": "una espada flamígera",
    "keywords": ["espada", "fuego", "flamígera"],
    "description": "Una espada mágica cuya hoja arde con llamas eternas. El calor es intenso pero no quema al portador.",
    "category": "arma",
    "tags": ["arma", "espada", "mágica", "fuego"],
    "attributes": {
        "damage": 15,
        "element": "fuego",
        "durability": 100,
        "magical": True,
        "enchantment_level": 3
    },
    "display": {
        "icon": "🔥"
    }
}
```

**Uso futuro**:
```python
# En un sistema de combate (futuro)
damage = item.attributes.get("damage", 1)
if item.attributes.get("element") == "fuego":
    damage *= 1.5
```

---

## Items con Locks (Restricciones)

El sistema de locks permite restringir quién puede interactuar con un objeto y cómo. La versión 2.0 introduce **locks contextuales** que permiten restricciones diferentes según la acción.

### Locks Simples (String)

Para restricciones que se aplican a todas las acciones:

```python
"espada_sagrada": {
    "name": "la Espada Sagrada Antigua",
    "keywords": ["espada", "sagrada", "antigua"],
    "description": "Una hoja legendaria que vibra con un poder inmenso. Solo los dignos pueden empuñarla.",
    "category": "arma",
    "tags": ["arma", "espada", "legendaria", "sagrada"],
    "locks": "rol(ADMIN)",  # Solo admins pueden cogerla
    "attributes": {
        "damage": 50,
        "magical": True
    },
    "display": {
        "icon": "⚜️"
    }
}
```

### Locks Contextuales (Diccionario)

Para restricciones diferentes según el tipo de acción:

```python
"cofre_magico": {
    "name": "un cofre mágico",
    "keywords": ["cofre", "magico"],
    "description": "Un cofre ornamentado con runas brillantes.",
    "is_container": True,
    "capacity": 10,

    # Locks contextuales: diferentes restricciones por acción
    "locks": {
        "get": "rol(SUPERADMIN)",              # Solo SUPERADMIN puede cogerlo (muy pesado)
        "put": "tiene_objeto(llave_magica)",   # Necesita llave para meter cosas
        "take": "tiene_objeto(llave_magica)"   # Necesita llave para sacar cosas
    },

    # Mensajes de error personalizados (opcional)
    "lock_messages": {
        "get": "El cofre está encantado y firmemente fijado al suelo.",
        "put": "El cofre está sellado con magia. Necesitas la llave mágica.",
        "take": "El cofre está sellado con magia. Necesitas la llave mágica."
    },

    "display": {
        "icon": "📦✨"
    }
}
```

### Funciones de Lock Disponibles

**Basadas en Roles:**
- `rol(ADMIN)` - Solo admin o superior
- `rol(SUPERADMIN)` - Solo superadmin

**Basadas en Inventario:**
- `tiene_objeto(llave_especial)` - Requiere objeto específico
- `cuenta_items(5)` - Requiere tener al menos N items
- `tiene_item_categoria(arma)` - Requiere tener item de categoría
- `tiene_item_tag(magico)` - Requiere tener item con tag

**Basadas en Ubicación:**
- `en_sala(plaza_central)` - Solo en sala específica
- `en_categoria_sala(templo)` - Solo en salas de categoría
- `tiene_tag_sala(sagrado)` - Solo en salas con tag

**Basadas en Estado:**
- `online()` - Solo si el personaje está conectado

**Combinaciones:**
- `rol(ADMIN) or tiene_objeto(permiso)` - Operador OR
- `rol(ADMIN) and tiene_objeto(llave)` - Operador AND
- `not cuenta_items(10)` - Operador NOT
- `(rol(ADMIN) or tiene_objeto(llave)) and online()` - Expresiones complejas

Ver: `docs/sistemas-del-motor/sistema-de-permisos.md` para documentación completa sobre locks.

---

## Contenedores

Los contenedores permiten a los jugadores almacenar objetos dentro de otros objetos.

### Contenedor Portátil (Mochila)

```python
"mochila_cuero": {
    "name": "una mochila de cuero",
    "keywords": ["mochila", "cuero", "mochila de cuero"],
    "description": "Una mochila simple pero resistente, hecha de cuero curtido.",
    "category": "contenedor",
    "tags": ["contenedor", "mochila", "portátil"],
    "is_container": True,
    "capacity": 10,  # Puede contener hasta 10 items
    "display": {
        "icon": "🎒"
    }
}
```

**Uso**:
```
/coger mochila
/meter espada mochila
/sacar espada mochila
/inv mochila
```

### Contenedor Fijo (Cofre)

Para crear un contenedor que NO se puede coger pero es accesible:

```python
"cofre_roble": {
    "name": "un cofre de roble",
    "keywords": ["cofre", "roble", "cofre de roble"],
    "description": "Un pesado cofre de madera con refuerzos de hierro.",
    "category": "contenedor",
    "tags": ["contenedor", "cofre", "fijo"],
    "is_container": True,
    "capacity": 20,

    # Locks contextuales: fijo pero accesible
    "locks": {
        "get": "rol(SUPERADMIN)",  # No se puede coger (muy pesado)
        "put": "",                  # Todos pueden meter cosas
        "take": ""                  # Todos pueden sacar cosas
    },

    "lock_messages": {
        "get": "El cofre es demasiado pesado para levantarlo. Está firmemente anclado al suelo."
    },

    "display": {
        "icon": "📦"
    }
}
```

**Resultado**:
- `/coger cofre` → "El cofre es demasiado pesado para levantarlo..."
- `/meter espada cofre` → Funciona (sin restricción)
- `/sacar espada cofre` → Funciona (sin restricción)
- El cofre permanece en la sala

### Contenedor con Llave

Para crear un cofre que requiere una llave para acceder:

```python
"cofre_cerrado": {
    "name": "un cofre cerrado con llave",
    "keywords": ["cofre", "cerrado"],
    "description": "Un cofre de hierro con una cerradura compleja.",
    "category": "contenedor",
    "tags": ["contenedor", "cofre", "cerrado", "fijo"],
    "is_container": True,
    "capacity": 15,

    # Locks contextuales: fijo y cerrado
    "locks": {
        "get": "rol(SUPERADMIN)",                   # No se puede coger
        "put": "tiene_objeto(llave_cofre) or rol(ADMIN)",   # Necesita llave para meter
        "take": "tiene_objeto(llave_cofre) or rol(ADMIN)"   # Necesita llave para sacar
    },

    "lock_messages": {
        "get": "El cofre está encadenado al suelo.",
        "put": "El cofre está cerrado con llave. Necesitas la llave del cofre.",
        "take": "El cofre está cerrado con llave. Necesitas la llave del cofre."
    },

    "display": {
        "icon": "🔒"
    }
}
```

**Uso**:
- Sin llave: `/meter espada cofre` → "El cofre está cerrado con llave..."
- Con llave: `/meter espada cofre` → Funciona
- Como admin: Acceso automático (bypass del lock)

---

## Items que Otorgan Comandos

Los items pueden otorgar comandos adicionales cuando están en el inventario del jugador:

```python
"pico_minero": {
    "name": "un pico de minero",
    "keywords": ["pico", "minero"],
    "description": "Un pico pesado y resistente, ideal para extraer minerales.",
    "category": "herramienta",
    "tags": ["herramienta", "minería"],
    "grants_command_sets": ["mining"],  # Otorga comandos de minería
    "display": {
        "icon": "⛏️"
    }
}
```

**Resultado**: Mientras el jugador tenga el pico en su inventario, tendrá acceso a comandos como `/minar`, `/extraer`, etc. (si el CommandSet `mining` está implementado).

**Nota**: El CommandSet `mining` debe estar definido en `commands/player/mining.py` y registrado en el dispatcher.

---

## Items con Scripts Reactivos (Sistema de Eventos)

Los scripts reactivos responden a eventos del jugador usando el Sistema de Eventos. Cada evento tiene fases BEFORE (puede cancelar) y AFTER (efectos).

### Items que Responden a ON_LOOK

```python
"amuleto_magico": {
    "name": "un amuleto mágico",
    "keywords": ["amuleto", "mágico", "amuleto mágico"],
    "description": "Una joya opaca que parece absorber la luz a su alrededor.",
    "category": "joyería",
    "tags": ["mágico", "joyería"],
    "scripts": {
        "after_on_look": [{
            "script": "script_notificar_brillo_magico(color=púrpura)",
            "priority": 0
        }]
    },
    "display": {
        "icon": "💎"
    }
}
```

**Resultado**: Cuando un jugador use `/mirar amuleto`, verá la descripción normal Y recibirá un mensaje adicional privado: *"Notas que emite un suave brillo de color púrpura."*

### Items que Responden a ON_PUT y ON_TAKE

Estos eventos se disparan cuando un jugador mete o saca objetos de contenedores.

#### Ejemplo: Item que no puede guardarse

```python
"espada_maldita": {
    "name": "una espada maldita",
    "description": "La hoja emite un brillo maligno...",
    "category": "arma",
    "tags": ["arma", "espada", "maldita"],
    "scripts": {
        "before_on_put": [{
            "script": "cancel_action(mensaje='La espada maldita se resiste a ser guardada')",
            "priority": 10
        }]
    },
    "display": {
        "icon": "⚔️"
    }
}
```

**Resultado**: Si intentas `/meter espada mochila`, el comando se cancela y ves el mensaje: *"La espada maldita se resiste a ser guardada"*

#### Ejemplo: Contenedor que reacciona a objetos guardados

```python
"cofre_magico": {
    "name": "un cofre mágico",
    "keywords": ["cofre", "magico"],
    "description": "Un cofre ornamentado con runas brillantes.",
    "category": "contenedor",
    "tags": ["contenedor", "mágico"],
    "is_container": True,
    "capacity": 10,
    "scripts": {
        "after_on_put": [{
            "script": "broadcast_room(mensaje='El cofre brilla al recibir un objeto')",
            "priority": 0
        }]
    },
    "display": {
        "icon": "📦✨"
    }
}
```

**Resultado**: Cuando alguien usa `/meter espada cofre`, todos los jugadores en la sala ven: *"El cofre brilla al recibir un objeto"*

### Items que Responden a ON_USE (Items Usables)

El comando `/usar` es completamente script-driven. **Toda la lógica** de qué hace un objeto al usarse está en los scripts.

#### Ejemplo: Poción Curativa Simple

```python
"pocion_vida": {
    "name": "una poción de vida",
    "keywords": ["poción", "vida", "pocion vida"],
    "description": "Un frasco con líquido rojo brillante. Huele a hierbas medicinales.",
    "category": "consumible",
    "tags": ["poción", "consumible", "curación"],
    "scripts": {
        "after_on_use": [{
            "script": "global:curar_personaje(cantidad=50, mensaje='Te sientes revitalizado')",
            "priority": 0
        }]
    },
    "display": {
        "icon": "🧪"
    }
}
```

**Resultado**: Al usar `/usar pocion`, el jugador se cura 50 HP y recibe el mensaje: *"Te sientes revitalizado"*

#### Ejemplo: Item Consumible con Usos Limitados

```python
"anillo_deseos": {
    "name": "un anillo de los deseos",
    "keywords": ["anillo", "deseos"],
    "description": "Un anillo antiguo con tres gemas. Dicen que puede cumplir tres deseos.",
    "category": "joyería",
    "tags": ["joyería", "mágico", "consumible"],
    "scripts": {
        "before_on_use": [{
            "script": """
# Verificar usos restantes (estado persistente)
usos = await state_service.get_persistent(session, target, 'usos', default=3)
if usos <= 0:
    return False  # Cancelar acción
return True
""",
            "cancel_message": "El anillo ha perdido todo su poder. No quedan deseos.",
            "priority": 10
        }],
        "after_on_use": [{
            "script": """
# Decrementar usos
usos = await state_service.get_persistent(session, target, 'usos', default=3)
await state_service.set_persistent(session, target, 'usos', usos - 1)

# Curar 100 HP
character.hp = min(character.hp + 100, character.max_hp)
await broadcaster_service.send_message_to_character(
    character,
    f'✨ El anillo brilla intensamente y te sientes completamente restaurado. (Quedan {usos - 1} usos)'
)

# Si era el último uso, cambiar descripción
if usos - 1 <= 0:
    await state_service.set_persistent(session, target, 'agotado', True)
""",
            "priority": 0
        }]
    },
    "display": {
        "icon": "💍"
    }
}
```

**Resultado**: Cada uso cura 100 HP y consume un uso. Después de 3 usos, el anillo deja de funcionar.

#### Ejemplo: Item que Otorga Buff Temporal

```python
"elixir_fuerza": {
    "name": "un elixir de fuerza",
    "keywords": ["elixir", "fuerza"],
    "description": "Una poción densa con un brillo dorado.",
    "category": "consumible",
    "tags": ["consumible", "buff", "temporal"],
    "scripts": {
        "after_on_use": [{
            "script": """
# Otorgar buff temporal (30 minutos)
from datetime import timedelta
await state_service.set_transient(character, 'fuerza_aumentada', True, ttl=timedelta(minutes=30))

# Notificar jugador
await broadcaster_service.send_message_to_character(
    character,
    '<i>Sientes una oleada de fuerza sobrehumana recorrer tu cuerpo.</i>'
)

# Destruir item (consumible)
await session.delete(target)
await session.flush()
""",
            "priority": 0
        }]
    },
    "display": {
        "icon": "🧪"
    }
}
```

**Resultado**: Al usar `/usar elixir`, el jugador recibe un buff de 30 minutos y el item se destruye.

### Eventos Disponibles para Items

| Evento | Cuándo se Dispara | Uso Común |
|--------|------------------|-----------|
| `ON_LOOK` | `/mirar <item>` | Mensajes descriptivos, efectos visuales |
| `ON_GET` | `/coger <item>` | Validaciones, trampas, efectos al coger |
| `ON_DROP` | `/dejar <item>` | Efectos al soltar, notificaciones |
| `ON_PUT` | `/meter <item> en <contenedor>` | Prevenir guardado, reacciones del contenedor |
| `ON_TAKE` | `/sacar <item> de <contenedor>` | Purificaciones, activaciones |
| `ON_USE` | `/usar <item>` | **Lógica completa de uso** (pociones, pergaminos, etc.) |

Ver: `docs/sistemas-del-motor/sistema-de-eventos.md` para documentación completa sobre eventos y scripts.

---

## Items con Scripts Proactivos (Tick Scripts)

Los tick scripts permiten que los objetos actúen por sí solos periódicamente usando el sistema de scheduling:

```python
"craneo_susurrante": {
    "name": "un cráneo susurrante",
    "keywords": ["cráneo", "calavera", "susurrante"],
    "description": "Un cráneo amarillento que parece murmurar cuando no lo miras directamente.",
    "category": "mágico",
    "tags": ["mágico", "maldito", "inquietante"],
    "tick_scripts": [
        {
            "interval_ticks": 150,  # Cada 5 minutos (150 ticks * 2s)
            "script": "script_espada_susurra_secreto",
            "category": "ambient",
            "permanent": True  # Se repite indefinidamente
        }
    ],
    "display": {
        "icon": "💀"
    }
}
```

**Resultado**: Cada 5 minutos, todos los jugadores online en la misma sala que el cráneo recibirán un mensaje privado con un "secreto" aleatorio.

**Cálculo de ticks** (con tick predeterminado de 2s):
- 10 segundos → `10 / 2 = 5 ticks`
- 1 minuto → `60 / 2 = 30 ticks`
- 5 minutos → `300 / 2 = 150 ticks`
- 1 hora → `3600 / 2 = 1800 ticks`

Ver: `docs/sistemas-del-motor/sistema-de-scheduling.md` y `docs/creacion-de-contenido/escritura-de-scripts.md`

---

## Íconos Personalizados

Personaliza el emoji que representa tu item:

```python
"pocion_vida": {
    "name": "una poción de vida",
    "keywords": ["poción", "vida", "pocion vida"],
    "description": "Un frasco con líquido rojo brillante. Huele a hierbas medicinales.",
    "category": "consumible",
    "tags": ["poción", "consumible", "curación"],
    "display": {
        "icon": "🧪"  # Ícono personalizado
    }
}
```

**Íconos comunes**:
- Armas: ⚔️ 🗡️ 🏹 🔫 🪓
- Armaduras: 🛡️ ⛑️ 👕
- Pociones: 🧪 🍾 🧉
- Joyas: 💍 💎 ⚜️
- Herramientas: ⛏️ 🔧 🔨 🪚
- Libros: 📚 📖 📜
- Llaves: 🔑 🗝️
- Contenedores: 🎒 📦 🧳 🗃️

Ver: `src/templates/icons.py` para la lista completa.

---

## Ejemplo Completo: Item Avanzado

Aquí hay un ejemplo mostrando todas las características:

```python
"espada_viviente": {
    # Información básica
    "name": "la Espada Viviente",
    "keywords": ["espada", "viviente", "espada viviente"],
    "description": "La hoja de acero parece retorcerse y moverse por cuenta propia. Un ojo carmesí brilla en la empuñadura, observando todo a su alrededor.",

    # Organización
    "category": "arma",
    "tags": ["arma", "espada", "mágica", "legendaria", "maldita"],

    # Restricciones
    "locks": "rol(ADMIN) or tiene_objeto(sello_vinculacion)",

    # Atributos de juego
    "attributes": {
        "damage": 35,
        "magical": True,
        "element": "oscuridad",
        "durability": 999,
        "enchantment_level": 5,
        "sentient": True,
        "alignment": "caótico"
    },

    # Funcionalidad
    "grants_command_sets": ["sword_mastery", "dark_magic"],

    # Comportamiento reactivo
    "scripts": {
        "on_look": "script_espada_viviente_mirada"
    },

    # Comportamiento proactivo
    "tick_scripts": [
        {
            "interval_ticks": 300,  # Cada 10 minutos
            "script": "script_espada_susurra_secreto",
            "category": "ambient",
            "permanent": True
        }
    ],

    # Personalización de display
    "display": {
        "icon": "🗡️",
        "template": "legendary_item.html.j2"  # Template personalizado
    }
}
```

---

## Generando Items en el Juego

### Como Administrador

**Comando principal**: `/generarobjeto <item_key>`

```
/generarobjeto espada_hierro
→ Crea la espada en tu inventario

/generarobjeto mochila_cuero
→ Crea la mochila en tu inventario

/generarobjeto cofre_roble
→ Crea el cofre en la sala actual (ya que no se puede coger)
```

### Colocando Items en Salas

1. Genera el objeto en tu inventario
2. Usa `/dejar <objeto>` para dejarlo en la sala

Alternativamente, puedes crear scripts que generen objetos en salas específicas al iniciar el mundo.

---

## Usando Categorías y Etiquetas

Las categorías y etiquetas ayudan a organizar y filtrar items:

```python
"espada_elfica": {
    "name": "una espada élfica",
    "keywords": ["espada", "élfica", "elfa"],
    "description": "Una hoja elegante forjada por artesanos élficos.",
    "category": "arma_élfica",  # Categoría principal
    "tags": ["arma", "espada", "élfica", "mágica", "ligera", "rara"],  # Múltiples etiquetas
    "display": {
        "icon": "⚔️"
    }
}
```

**Uso**:
- Comando admin: `/listaritems cat:arma_élfica`
- Comando admin: `/listaritems tag:mágica`
- Filtrado por sistemas futuros (tiendas, crafteo, etc.)

Ver: `docs/sistemas-del-motor/categorias-y-etiquetas.md` para documentación completa.

---

## Patrones Comunes

### Arma Básica

```python
"daga_hierro": {
    "name": "una daga de hierro",
    "keywords": ["daga", "hierro"],
    "description": "Una daga corta y afilada.",
    "category": "arma",
    "tags": ["arma", "daga", "común"],
    "attributes": {"damage": 5},
    "display": {"icon": "🗡️"}
}
```

### Poción Consumible

```python
"pocion_mana": {
    "name": "una poción de maná",
    "keywords": ["poción", "mana", "azul"],
    "description": "Líquido azul brillante que restaura energía mágica.",
    "category": "consumible",
    "tags": ["poción", "consumible", "maná"],
    "attributes": {"restore_mana": 50, "consumable": True},
    "display": {"icon": "🧪"}
}
```

### Llave de Quest

```python
"llave_torre": {
    "name": "la llave de la torre",
    "keywords": ["llave", "torre", "llave torre"],
    "description": "Una llave antigua de bronce con grabados arcanos.",
    "category": "llave",
    "tags": ["llave", "quest", "único"],
    "display": {"icon": "🗝️"}
}
```

### Libro de Conocimiento

```python
"grimorio_fuego": {
    "name": "el Grimorio de las Llamas",
    "keywords": ["grimorio", "libro", "fuego"],
    "description": "Un tomo antiguo cuyas páginas parecen arder sin consumirse.",
    "category": "libro",
    "tags": ["libro", "mágico", "fuego", "grimorio"],
    "grants_command_sets": ["fire_magic"],
    "display": {"icon": "📕"}
}
```

### Moneda o Gema

```python
"moneda_oro": {
    "name": "una moneda de oro",
    "keywords": ["moneda", "oro", "dinero"],
    "description": "Una brillante moneda de oro del reino.",
    "category": "moneda",
    "tags": ["moneda", "económico", "oro"],
    "attributes": {"value": 100, "stackable": True},
    "display": {"icon": "💰"}
}
```

---

## Mejores Prácticas

1. **Usa claves descriptivas** - `"espada_fuego"` no `"item_23"`
2. **Incluye múltiples keywords** - Facilita que los jugadores encuentren el objeto
3. **Escribe descripciones evocativas** - 2-3 frases, lenguaje inmersivo
4. **Categoriza apropiadamente** - Ayuda con organización y filtrado
5. **Etiqueta generosamente** - Facilita búsquedas y características futuras
6. **Atributos para datos de juego** - Damage, durability, value, etc.
7. **Locks para items especiales** - Protege items poderosos o únicos
8. **Contenedores con capacidad realista** - 10-20 para mochilas, 20-50 para cofres
9. **Scripts para comportamiento único** - Hace que items legendarios sean memorables
10. **Íconos apropiados** - Usa emojis que representen visualmente el objeto

---

## Solución de Problemas

### "El objeto no se crea"
- Verifica sintaxis del diccionario Python
- Verifica que la clave sea única
- Mira los logs del bot para errores
- Reinicia el bot si modificaste `item_prototypes.py`

### "No puedo coger el objeto"
- Verifica el lock del objeto
- Verifica que no sea un contenedor fijo (lock = rol(SUPERADMIN))
- Verifica que tengas permisos o el objeto requerido

### "El contenedor no funciona"
- Verifica `"is_container": True`
- Verifica `"capacity"` está definido
- Verifica sintaxis de comandos: `/meter <item> <contenedor>`

### "Los comandos otorgados no aparecen"
- Verifica que el CommandSet esté implementado
- Verifica que el item esté en tu inventario
- El sistema revisa inventario para determinar comandos disponibles

### "El script no se ejecuta"
- Verifica que el script esté registrado en `script_service.py`
- Verifica sintaxis del script string
- Mira los logs para errores de ejecución de scripts

---

## Resumen

Creando items en Runegram:

1. Edita `game_data/item_prototypes.py`
2. Define item con clave única, nombre, keywords, descripción
3. Opcional: Agrega atributos, locks, comportamientos
4. Opcional: Haz contenedores con `is_container` + `capacity`
5. Opcional: Otorga comandos con `grants_command_sets`
6. Opcional: Agrega scripts reactivos o proactivos
7. Reinicia el bot si es necesario
8. Usa `/generarobjeto <key>` como admin para crear

¡Los items son las herramientas que dan vida y profundidad al mundo de Runegram. Crea objetos memorables que cuenten historias!

---

**Documentación Relacionada:**
- [Construyendo Salas](construccion-de-salas.md)
- [Escribiendo Scripts](escritura-de-scripts.md)
- [Sistema de Prototipos](../sistemas-del-motor/sistema-de-prototipos.md)
- [Sistema de Permisos](../sistemas-del-motor/sistema-de-permisos.md)
- [Categorías y Etiquetas](../sistemas-del-motor/categorias-y-etiquetas.md)
- [Sistema de Scheduling](../sistemas-del-motor/sistema-de-scheduling.md)
