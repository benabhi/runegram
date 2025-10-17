---
título: "Construyendo Salas en Runegram"
categoría: "Creación de Contenido"
audiencia: "creador-de-contenido"
versión: "1.0"
última_actualización: "2025-01-09"
autor: "Proyecto Runegram"
etiquetas: ["salas", "construcción-mundo", "prototipos", "salidas"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-prototipos.md"
  - "sistemas-del-motor/world-loader.md"
  - "creacion-de-contenido/creacion-de-items.md"
  - "primeros-pasos/filosofia-central.md"
referencias_código:
  - "game_data/room_prototypes.py"
  - "src/services/world_loader_service.py"
estado: "actual"
importancia: "alta"
---

# Construyendo Salas en Runegram

Gracias a la arquitectura dirigida por datos de Runegram, expandir el mundo del juego es una tarea de diseño de contenido, no de programación del motor. Esta guía te muestra cómo agregar nuevas salas, salidas con cerraduras y detalles interactivos simplemente editando archivos de datos en la carpeta `game_data/`.

## Archivo a Editar: `game_data/room_prototypes.py`

Todas las definiciones de salas viven en el diccionario `ROOM_PROTOTYPES` en este archivo. El `world_loader_service` lee este archivo al iniciar el bot para construir o sincronizar el mundo en la base de datos.

## Estructura de un Prototipo de Sala

```python
"unique_key": {
    "name": str,                    # Nombre de la sala mostrado a los jugadores
    "description": str,              # Texto principal mostrado al entrar
    "category": str,                 # Opcional: Categoría principal (ej: "ciudad_runegard")
    "tags": list[str],              # Opcional: Múltiples etiquetas (ej: ["exterior", "seguro"])
    "exits": dict,                   # Opcional: Conexiones a otras salas
    "grants_command_sets": list[str], # Opcional: CommandSets otorgados por esta sala
    "details": dict,                 # Opcional: Elementos examinables que no son items
    "display": {
        "icon": str,                 # Opcional: Emoji personalizado para esta sala
        "template": str              # Opcional: Template Jinja2 personalizado
    }
}
```

## Creando una Sala Básica

Vamos a crear una sala de taberna simple:

```python
# En game_data/room_prototypes.py

ROOM_PROTOTYPES = {
    # ... salas existentes ...

    "taverna_dragones": {
        "name": "La Taverna de los Tres Dragones",
        "description": "El aroma a cerveza y pan recién horneado llena este acogedor establecimiento. Varias mesas de madera desgastadas ocupan la sala, y un fuego crepita en la chimenea.",
        "category": "ciudad_runegard",
        "tags": ["ciudad", "interior", "social", "seguro"],
        "display": {
            "icon": "🍺"  # Ícono personalizado de taberna
        }
    }
}
```

## Conectando Salas con Salidas

**REGLA CRÍTICA**: Todas las salidas deben ser **BIDIRECCIONALES** y **EXPLÍCITAS**.

Si la sala A tiene salida "norte" → sala B, entonces la sala B **DEBE** tener salida explícita "sur" → sala A.

### Sintaxis de Salidas

Hay dos formas de definir una salida:

#### a) Sintaxis Simple (Sin Cerraduras)

Simplemente proporciona la clave de la sala destino como string:

```python
"plaza_central": {
    "name": "Plaza Central de Runegard",
    "exits": {
        "oeste": "biblioteca_antigua"  # Salida bidireccional simple
    }
},
"biblioteca_antigua": {
    "name": "Biblioteca Antigua",
    "exits": {
        "este": "plaza_central"  # Salida de retorno explícita
    }
}
```

**Nota**: Con la implementación actual, debes definir ambas salidas explícitamente. El sistema NO crea automáticamente salidas de retorno.

#### b) Sintaxis Avanzada (Con Cerraduras)

Para agregar una cerradura a una salida, usa un diccionario con las claves `"to"` y `"locks"`:

```python
"plaza_central": {
    "exits": {
        "norte": {
            "to": "armeria",
            "locks": "rol(ADMIN) and tiene_objeto(llave_armeria)"
        }
    }
},
"armeria": {
    "name": "La Armería de Runegard",
    "exits": {
        "sur": "plaza_central"  # La salida de retorno no tiene cerradura
    }
}
```

**Importante**: Cuando usas sintaxis avanzada, la cerradura se aplica **solo a la salida de salida**. La salida de retorno se crea sin cerradura (si se define explícitamente).

**Resultado**: Un jugador puede salir libremente de la armería al sur, pero para entrar desde la plaza al norte, debe pasar la verificación de cerradura.

### Ejemplo: Conexión Bidireccional Completa

```python
"plaza_central": {
    "name": "Plaza Central de Runegard",
    "exits": {
        "norte": "calle_mercaderes",
        "este": "taverna_dragones",
        "sur": "limbo"
    }
},
"calle_mercaderes": {
    "name": "Calle de los Mercaderes",
    "exits": {
        "sur": "plaza_central"  # Retorno desde el norte
    }
},
"taverna_dragones": {
    "name": "La Taverna de los Tres Dragones",
    "exits": {
        "oeste": "plaza_central"  # Retorno desde el este
    }
},
"limbo": {
    "name": "El Limbo",
    "exits": {
        "norte": "plaza_central"  # Retorno desde el sur
    }
}
```

## Agregando Detalles Interactivos

Los detalles son elementos que no son items en una sala que los jugadores pueden examinar con `/mirar`, pero no pueden recoger.

```python
"plaza_central": {
    "name": "Plaza Central de Runegard",
    "description": "Estás en el corazón de la ciudad. Una imponente fuente de mármol domina el centro de la plaza.",
    "details": {
        "fuente_plaza": {
            "keywords": ["fuente", "marmol", "fuente de marmol"],
            "description": "Es una magnífica fuente esculpida en mármol blanco. El agua cristalina fluye desde la boca de tres leones de piedra. En el fondo, puedes ver el brillo de algunas monedas arrojadas por los transeúntes."
        },
        "leones": {
            "keywords": ["leones", "leon", "estatuas"],
            "description": "Tres leones de piedra rodean la fuente, sus fauces abiertas vierten agua constantemente."
        }
    }
}
```

**Resultado**:
- `/mirar fuente` muestra la descripción de la fuente
- `/mirar leones` muestra la descripción de los leones
- Estos NO son items, solo elementos descriptivos

## Usando Categorías y Etiquetas

Las categorías y etiquetas ayudan a organizar y filtrar salas:

```python
"bosque_oscuro_entrada": {
    "name": "Entrada al Bosque Oscuro",
    "description": "Los árboles aquí son antiguos y retorcidos, bloqueando casi toda la luz del sol.",
    "category": "bosque_oscuro",  # Categoría principal
    "tags": ["exterior", "peligroso", "bosque", "sombrio"],  # Múltiples etiquetas
}
```

**Uso**:
- Comando admin: `/listarsalas cat:bosque_oscuro`
- Comando admin: `/listarsalas tag:peligroso`

Ver: `docs/sistemas-del-motor/categorias-y-etiquetas.md` para documentación completa.

## Otorgando CommandSets por Sala

Las salas pueden otorgar comandos adicionales a los jugadores mientras estén presentes:

```python
"forja_del_enano": {
    "name": "La Forja del Enano Errante",
    "description": "El calor del fuego y el rítmico martilleo sobre el yunque llenan esta sala. Herramientas de herrería cubren las paredes.",
    "grants_command_sets": ["smithing"],  # Los jugadores ganan comandos de herrería aquí
    "exits": {
        "sur": "plaza_central"
    }
}
```

**Resultado**: Mientras estén en esta sala, los jugadores tienen acceso a comandos de herrería como `/forjar`, `/reparar`, etc.

**Nota**: El `smithing` CommandSet debe estar definido en `commands/player/smithing.py` y registrado en el dispatcher.

## Íconos y Templates Personalizados

Personaliza cómo se muestra una sala:

```python
"trono_del_rey": {
    "name": "Sala del Trono",
    "description": "Un majestuoso salón real con techos altísimos y columnas de mármol.",
    "display": {
        "icon": "👑",  # Ícono personalizado del trono en lugar del ícono predeterminado de sala
        "template": "throne_room.html.j2"  # Opcional: template Jinja2 personalizado
    }
}
```

**Ubicación del template**: `src/templates/base/throne_room.html.j2`

Ver: `docs/creacion-de-contenido/guia-de-estilo-de-salida.md` para creación de templates.

## Salas Reactivas con Scripts de Eventos

Las salas pueden responder a las acciones de los jugadores usando el Sistema de Eventos v3.0. Esto permite crear salas dinámicas que reaccionan al movimiento de jugadores.

### Scripts ON_ENTER y ON_LEAVE

Las salas pueden ejecutar scripts cuando un jugador entra o sale:

```python
"arena_combate": {
    "name": "Arena de Combate",
    "description": "Un círculo de arena rodeado por gradas. No hay escapatoria una vez que entras.",
    "scripts": {
        "after_on_enter": [{
            "script": """
# Iniciar combate automáticamente
await state_service.set_persistent(session, character, 'in_combat', True)
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=room.id,
    message_text='<b>¡El combate ha comenzado! No puedes huir hasta que termine.</b>'
)
""",
            "priority": 0
        }],
        "before_on_leave": [{
            "script": """
# Prevenir salida si está en combate
in_combat = await state_service.get_persistent(session, character, 'in_combat', default=False)
if in_combat:
    return False  # Cancelar movimiento
return True
""",
            "cancel_message": "¡No puedes huir del combate!",
            "priority": 10
        }]
    }
}
```

### Ejemplo: Sala con Trampa

```python
"cueva_oscura": {
    "name": "Cueva Oscura",
    "description": "Una cueva húmeda. Algo cruje bajo tus pies al entrar...",
    "scripts": {
        "after_on_enter": [{
            "script": """
# Verificar si la trampa ya fue activada
trampa_activada = await state_service.get_persistent(session, room, 'trampa_activada', default=False)

if not trampa_activada:
    # Daño al personaje
    character.attributes['hp'] = character.attributes.get('hp', 100) - 10
    await session.flush()

    # Marcar trampa como activada
    await state_service.set_persistent(session, room, 'trampa_activada', True)

    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=room.id,
        message_text='<i>¡Has activado una trampa! Pinchos emergen del suelo.</i>'
    )
""",
            "priority": 0
        }]
    }
}
```

### Ejemplo: Sala con Boss

```python
"camara_dragon": {
    "name": "Cámara del Dragón",
    "description": "Una vasta cámara llena de tesoros. Un dragón inmenso yace dormido.",
    "scripts": {
        "after_on_enter": [{
            "script": """
# Verificar si el dragón fue derrotado
dragon_muerto = await state_service.get_persistent(session, room, 'dragon_muerto', default=False)

if not dragon_muerto:
    await state_service.set_persistent(session, character, 'in_combat', True)
    await state_service.set_persistent(session, character, 'enemy', 'dragon_anciano')

    await broadcaster_service.send_message_to_room(
        session=session,
        room_id=room.id,
        message_text='<b>El dragón abre un ojo. "Intruso..." ruge con voz atronadora.</b>'
    )
""",
            "priority": 0
        }]
    }
}
```

**Ver:** `docs/sistemas-del-motor/sistema-de-eventos.md` para más ejemplos y detalles técnicos.

## Tick Scripts en Salas

Las salas pueden tener eventos periódicos usando el sistema de pulse:

```python
"camara_ritual": {
    "name": "Cámara de Ritual Antiguo",
    "description": "Símbolos arcanos brillan tenuemente en las paredes de esta cámara circular.",
    "tick_scripts": [
        {
            "interval_ticks": 150,  # Cada 5 minutos (150 ticks * 2s)
            "script": "script_ritual_glow",
            "category": "ambient",
            "permanent": True  # Se repite indefinidamente
        }
    ]
}
```

**Cálculo de ticks** (con pulse predeterminado de 2s):
- 10 segundos → `10 / 2 = 5 ticks`
- 1 minuto → `60 / 2 = 30 ticks`
- 5 minutos → `300 / 2 = 150 ticks`
- 1 hora → `3600 / 2 = 1800 ticks`

Ver: `docs/sistemas-del-motor/sistema-de-pulso.md` y `docs/creacion-de-contenido/escritura-de-scripts.md`

## Ejemplo de Sala Completo

Aquí hay un ejemplo completo mostrando todas las características:

```python
"biblioteca_arcana": {
    "name": "Biblioteca Arcana",
    "description": "Estantes interminables de libros antiguos se extienden hasta el techo abovedado. El silencio aquí es casi sagrado, roto solo por el ocasional paso de páginas.",

    # Organización
    "category": "ciudad_runegard",
    "tags": ["ciudad", "interior", "magico", "conocimiento", "silencioso"],

    # Navegación
    "exits": {
        "sur": "plaza_central",
        "arriba": {
            "to": "torre_archimago",
            "locks": "rol(ADMIN) or tiene_objeto(llave_torre)"
        }
    },

    # Detalles interactivos
    "details": {
        "estantes": {
            "keywords": ["estantes", "libros", "tomos"],
            "description": "Miles de libros cubren estos estantes, organizados por temas arcanos complejos. Reconoces tratados de invocación, taumaturgía y alquimia."
        },
        "globo": {
            "keywords": ["globo", "globo terraqueo", "esfera"],
            "description": "Un antiguo globo terráqueo gira lentamente sobre su eje, mostrando continentes que ya no existen."
        }
    },

    # Personalización de display
    "display": {
        "icon": "📚"
    },

    # La sala otorga comandos de estudio mágico
    "grants_command_sets": ["magic_study"],

    # Eventos periódicos ambientales
    "tick_scripts": [
        {
            "interval_ticks": 300,  # Cada 10 minutos
            "script": "script_biblioteca_susurro",
            "category": "ambient",
            "permanent": True
        }
    ]
}
```

## Sincronización del Mundo

Después de editar `room_prototypes.py`, reinicia el bot:

```bash
docker-compose restart
```

El `world_loader_service`:
1. Leerá los prototipos actualizados
2. Creará nuevas salas en la base de datos
3. Actualizará salas existentes si sus prototipos cambiaron
4. Creará/actualizará salidas automáticamente
5. Registrará todos los cambios

**Importante**: El world loader es **no destructivo**. No eliminará salas o salidas que existan en la base de datos pero no en los prototipos. Usa comandos de admin para limpiar manualmente si es necesario.

## Probando Tus Salas

Después de reiniciar:

1. `/teletransportar <room_key>` (como admin) - Ve a tu nueva sala
2. `/mirar` - Ve la descripción de la sala
3. `/mirar <detail_keyword>` - Prueba los detalles interactivos
4. Prueba salidas: `/norte`, `/sur`, etc.
5. `/listarsalas cat:<category>` - Verifica la categorización
6. `/examinarsala` (como admin) - Ve información técnica de la sala

## Patrones Comunes

### Sala Hub (Plaza Central)

```python
"plaza_central": {
    "name": "Plaza Central de Runegard",
    "description": "El corazón bullicioso de la ciudad.",
    "category": "ciudad_runegard",
    "tags": ["ciudad", "seguro", "social", "exterior"],
    "exits": {
        "norte": "calle_mercaderes",
        "sur": "limbo",
        "este": "taverna",
        "oeste": "biblioteca"
    },
    "display": {"icon": "🏛️"}
}
```

### Entrada a Zona Peligrosa

```python
"entrada_dungeon": {
    "name": "Entrada a las Mazmorras Oscuras",
    "description": "Un portal de piedra decrépita marca la entrada. Sientes un escalofrío.",
    "category": "dungeon_oscuro",
    "tags": ["exterior", "peligroso", "dungeon"],
    "exits": {
        "norte": "plaza_central",  # Salida segura
        "abajo": {
            "to": "dungeon_nivel_1",
            "locks": "nivel(5) or rol(ADMIN)"  # Requisito de nivel
        }
    },
    "display": {"icon": "🚪"}
}
```

### Sala de Tienda o Servicio

```python
"tienda_armaduras": {
    "name": "Armadurías del Norte",
    "description": "Armaduras de todo tipo cuelgan de las paredes. El herrero te saluda.",
    "category": "ciudad_runegard",
    "tags": ["ciudad", "comercio", "interior", "tienda"],
    "grants_command_sets": ["armor_shop"],  # Comandos de tienda disponibles aquí
    "exits": {
        "sur": "plaza_central"
    },
    "display": {"icon": "🛡️"}
}
```

### Sala Secreta

```python
"camara_secreta": {
    "name": "Cámara Secreta",
    "description": "Una sala oculta llena de tesoros antiguos y polvo.",
    "category": "ciudad_runegard",
    "tags": ["interior", "secreto", "tesoro"],
    "exits": {
        "arriba": "biblioteca_arcana"  # Solo alcanzable desde arriba
    },
    # No hay salida DESDE la biblioteca hacia aquí - debe ser revelada por puzzle/quest
    "display": {"icon": "🗝️"}
}
```

## Mejores Prácticas

1. **Siempre crea salidas bidireccionales explícitamente** - No confíes en la creación automática
2. **Usa claves descriptivas** - `"taverna_dragones"` no `"room_05"`
3. **Escribe descripciones inmersivas** - 2-3 frases, lenguaje evocativo
4. **Usa categorías para áreas principales** - `"ciudad_runegard"`, `"bosque_oscuro"`, etc.
5. **Etiqueta apropiadamente** - Ayuda con el filtrado y características futuras
6. **Agrega detalles para atmósfera** - Hace que el mundo se sienta vivo
7. **Bloquea áreas peligrosas** - Usa cerraduras `rol()` o `nivel()`
8. **Íconos personalizados para salas especiales** - Ayuda a la navegación visual
9. **Prueba todas las salidas** - Camina por cada conexión
10. **Nomenclatura consistente** - Español para nombres/descripciones, claves en minúsculas con guiones bajos

## Solución de Problemas

### "La salida no aparece"
- Verifica que ambas salas tengan definiciones de salida explícitas
- Verifica que las claves de sala coincidan exactamente (sensible a mayúsculas)
- Reinicia el bot después de los cambios

### "La cerradura no funciona"
- Verifica la sintaxis de cerradura: `"rol(ADMIN)"` o `"tiene_objeto(key)"`
- Verifica que la cerradura esté en el dict de salida, no en la sala
- Las cerraduras solo funcionan en sintaxis de salida avanzada

### "El detalle no se muestra"
- Verifica que las keywords estén en minúsculas
- Verifica que el detalle esté en el dict `"details"`
- Asegúrate de que `/mirar <keyword>` coincida con una de las keywords de la lista

### "La sala no se carga"
- Verifica errores de sintaxis en el dict de Python
- Mira los logs del bot para errores de world_loader
- Verifica que la clave de sala sea única

## Resumen

Construyendo salas en Runegram:

1. Edita `game_data/room_prototypes.py`
2. Define sala con clave, nombre, descripción
3. Agrega salidas bidireccionales explícitamente
4. Opcional: Agrega detalles, categorías, etiquetas, íconos
5. Opcional: Agrega cerraduras a salidas para restricciones
6. Opcional: Otorga command sets o agrega tick scripts
7. Reinicia el bot para cargar cambios
8. Prueba en el juego

¡El mundo es tu lienzo. Construye espacios inmersivos y conectados que cuenten una historia!

---

**Documentación Relacionada:**
- [Creando Items](creacion-de-items.md)
- [Escribiendo Scripts](escritura-de-scripts.md)
- [Sistema de Prototipos](../sistemas-del-motor/sistema-de-prototipos.md)
- [Servicio World Loader](../sistemas-del-motor/world-loader.md)
- [Categorías y Etiquetas](../sistemas-del-motor/categorias-y-etiquetas.md)
- [Sistema de Pulse](../sistemas-del-motor/sistema-de-pulso.md)
