# 🏛️ Plan: Sistema de Fixtures (Objetos de Ambiente)

**Fecha:** 2025-10-18
**Objetivo:** Implementar sistema de objetos fijos que forman parte del ambiente de las salas, diferenciándolos de items regulares mientras aprovechan toda la infraestructura existente.

---

## 📊 Análisis del Sistema Actual

### ✅ Infraestructura Ya Implementada

El proyecto **ya tiene implementado el 90% de lo necesario**:

1. **Sistema de Locks Contextuales** ✅
   - Locks diferentes por tipo de acción (`get`, `drop`, `put`, `take`, etc.)
   - Mensajes de error personalizados (`lock_messages`)
   - 9 lock functions incluyendo `rol(SUPERADMIN)`

2. **Sistema de Scripts y Eventos** ✅
   - Eventos BEFORE/AFTER para ON_LOOK, ON_GET, etc.
   - Scripts reactivos con prioridades
   - Scheduling (tick-based y cron-based)
   - State service (persistente y transiente)

3. **Sistema de Detalles de Sala** ✅
   - `details` en prototipos de sala
   - Comando `/mirar <detalle>` funcional
   - Descripciones inmersivas sin objetos físicos

4. **Template System** ✅
   - Templates Jinja2 para presentación
   - Separación de ítems, personajes, salidas
   - Sistema de íconos personalizable

### ❌ Única Carencia Detectada

**Falta una manera de diferenciar visualmente entre:**
- **Items regulares**: Objetos que pueden cogerse/moverse (aparecen en "Cosas a la vista")
- **Fixtures**: Objetos parte del ambiente, interactuables pero fijos (deberían aparecer integrados en la descripción)

---

## 🎯 Solución Propuesta: Flag `is_fixture`

### Concepto

Agregar una flag opcional `is_fixture: True` a los prototipos de items que:

1. **Los marca como parte del ambiente de la sala**
2. **Los excluye de la sección "Cosas a la vista"**
3. **Los muestra integrados en la descripción de la sala**
4. **Mantiene TODA su funcionalidad** (locks, scripts, eventos, estado)

### Ventajas de Esta Solución

✅ **Mínima invasión**: Solo requiere modificar template y agregar flag
✅ **Retrocompatible**: Items existentes sin la flag funcionan igual
✅ **Escalable**: Usa toda la infraestructura existente
✅ **Flexible**: Combina con locks, scripts y eventos sin conflictos
✅ **Consistente**: Sigue filosofía motor/contenido del proyecto

---

## 🔧 Plan de Implementación

### FASE 0: Extender World Loader para Sincronizar Fixtures (AUTOMÁTICO)

**Archivos**:
- `src/services/world_loader_service.py` - Agregar sincronización de fixtures
- `game_data/room_prototypes.py` - Agregar campo `fixtures` a salas

**Objetivo**: Permitir que los fixtures se definan en los prototipos de sala y se creen automáticamente al arrancar el bot (igual que las salas y salidas).

**Respuesta a la pregunta del usuario**: ¡SÍ, ES POSIBLE Y MUY ELEGANTE! No necesitas ir sala por sala creando fixtures manualmente con `/generarobjeto`. Los fixtures se definen en `room_prototypes.py` (campo `fixtures`) y se sincronizan automáticamente al arrancar.

**Cambios**:

1. **Agregar nuevo paso en `sync_world_from_prototypes()`**: Paso 4 - Sincronizar Fixtures

```python
async def sync_world_from_prototypes(session: AsyncSession):
    """
    Sincroniza la base de datos con los prototipos de salas.
    """
    logging.info("Sincronizando el mundo estático desde los prototipos...")
    try:
        # --- PASO 1: Sincronizar Salas --- (existente)
        room_key_to_id_map = {}
        # ... código existente ...

        # --- PASO 2: Limpiar Salidas Viejas --- (existente)
        # ... código existente ...

        # --- PASO 3: Crear Salidas Nuevas con Locks --- (existente)
        # ... código existente ...

        # --- PASO 4: Sincronizar Fixtures de Salas --- (NUEVO)
        logging.info("  -> Sincronizando fixtures de salas...")
        await _sync_room_fixtures(session, room_key_to_id_map)

        await session.commit()
        logging.info("¡Sincronización del mundo completada!")
    except Exception:
        logging.exception("Error fatal durante la sincronización del mundo.")
        raise


async def _sync_room_fixtures(session: AsyncSession, room_key_to_id_map: dict):
    """
    Sincroniza los fixtures definidos en prototipos de sala.

    Para cada sala que tenga campo 'fixtures', verifica que existan
    los items correspondientes. Si no existen, los crea.
    Si ya existen, los mantiene (preserva su estado persistente).
    """
    from src.models.item import Item
    from game_data.item_prototypes import ITEM_PROTOTYPES

    for room_key, room_data in ROOM_PROTOTYPES.items():
        fixture_keys = room_data.get("fixtures", [])

        if not fixture_keys:
            continue

        room_id = room_key_to_id_map.get(room_key)
        if not room_id:
            continue

        for item_key in fixture_keys:
            # Verificar que el prototipo de item existe
            if item_key not in ITEM_PROTOTYPES:
                logging.warning(
                    f"  -> Fixture '{item_key}' definido en sala '{room_key}' "
                    f"no existe en ITEM_PROTOTYPES. Se ignora."
                )
                continue

            # Verificar si el fixture ya existe en esta sala
            result = await session.execute(
                select(Item).where(
                    Item.key == item_key,
                    Item.room_id == room_id
                )
            )
            existing_fixture = result.scalar_one_or_none()

            if existing_fixture:
                # Ya existe, mantenerlo (preserva script_state)
                logging.debug(
                    f"  -> Fixture '{item_key}' ya existe en '{room_key}'. "
                    f"Mantenido (ID: {existing_fixture.id})."
                )
            else:
                # No existe, crearlo
                new_fixture = Item(key=item_key, room_id=room_id)
                session.add(new_fixture)
                logging.info(
                    f"  -> Creado fixture '{item_key}' en sala '{room_key}'."
                )
```

**Formato en prototipos de sala**:

```python
# game_data/room_prototypes.py
"plaza_central": {
    "name": "Plaza Central de Runegard",
    "description": "Estás en el corazón de la ciudad...",
    "category": "ciudad_runegard",
    "tags": ["ciudad", "seguro", "social"],

    # NUEVO CAMPO: Lista de fixtures que deben existir en esta sala
    "fixtures": [
        "fuente_magica_plaza",
        "arbol_frutal_plaza",
        "estatua_dios_guerra"
    ],

    "exits": {
        "sur": "limbo",
        "este": "calle_mercaderes"
    }
}
```

**Ventajas**:
- ✅ **Declarativo**: Fixtures definidos junto con la sala
- ✅ **Automático**: Se crean al arrancar (no hay que usar `/generarobjeto`)
- ✅ **Idempotente**: Reiniciar el bot no duplica fixtures
- ✅ **Preserva estado**: Fixtures existentes mantienen `script_state`
- ✅ **Consistente**: Misma filosofía que salas y salidas

**Comportamiento**:
- Al arrancar bot → `sync_world_from_prototypes()` se ejecuta
- Para cada sala con campo `fixtures`:
  - Verifica si fixture existe en BD
  - Si NO existe → crea nueva instancia de Item
  - Si existe → lo mantiene intacto (¡preserva estado!)
- Los fixtures usan sus prototipos de `item_prototypes.py`

---

### FASE 1: Modificar Template de Sala (VISUAL)

**Archivo**: `src/templates/base/room.html.j2`

**Cambios**:

1. **Después de la descripción de la sala**, agregar sección de fixtures:
```jinja2
<pre>{{ icon('room') }} <b>{{ room.name|upper }}</b>
{{ room.description|trim }}

{#- NUEVO: Mostrar fixtures integrados en el ambiente -#}
{%- set fixtures = room.items|selectattr('prototype.is_fixture', 'equalto', true)|list %}
{%- if fixtures %}
{%- for fixture in fixtures %}
{%- set fixture_icon = fixture.prototype.get('display', {}).get('icon', '') %}
{{ fixture_icon }} {{ fixture.get_name()|capitalize }}
{%- endfor %}

{%- endif %}

{#- Filtrar fixtures de "Cosas a la vista" -#}
{%- set regular_items = room.items|rejectattr('prototype.is_fixture', 'equalto', true)|list %}
{%- if regular_items %}

{{ icon('look') }} <b>Cosas a la vista:</b>
{%- for item in regular_items %}
{%- set item_icon = item.prototype.get('display', {}).get('icon', icon('item')) %}
    {{ loop.index }}. {{ item_icon }} {{ item.get_name() }}
{%- endfor %}
{%- endif %}
```

**Resultado visual**:
```
🏛️ PLAZA CENTRAL DE RUNEGARD
Estás en el corazón de la ciudad. El bullicio de mercaderes...

⛲ Una magnífica fuente de mármol
🌳 Un antiguo árbol de roble
🗿 Una estatua de bronce del fundador

🔍 Cosas a la vista:
    1. ⚔️ una espada oxidada
    2. 📜 un pergamino arrugado

👥 Personajes:
    - 🧙 Gandalf
    - ⚔️ Aragorn

🚪 Salidas:
    - ⬆️ Norte (Calle de los Mercaderes)
    - ⬇️ Sur (El Limbo)
```

---

### FASE 2: Crear Prototipos de Ejemplo

**Archivos**:
- `game_data/item_prototypes.py` - Definir prototipos de fixtures
- `game_data/room_prototypes.py` - Agregar campo `fixtures` a salas

**Ejemplos de fixtures con diferentes comportamientos**:

#### Ejemplo 1: Árbol con Frutas (Scheduling + Estado)

```python
"arbol_frutal_plaza": {
    "name": "un árbol frutal",
    "keywords": ["arbol", "frutal", "arbol frutal", "roble"],
    "description": "Un majestuoso roble que ha visto pasar generaciones. Sus ramas están cargadas de brillantes manzanas doradas.",
    "category": "ambiente",
    "is_fixture": True,  # ← NUEVA FLAG

    # Lock: No se puede coger el árbol
    "locks": {
        "get": "rol(SUPERADMIN)"
    },
    "lock_messages": {
        "get": "El árbol está firmemente arraigado en la tierra. No puedes arrancarlo."
    },

    # Script: Genera una fruta cada 5 minutos
    "scheduled_scripts": [
        {
            "schedule": "*/5 * * * *",  # Cada 5 minutos
            "script": "script_generar_fruta_en_sala(item_key=manzana_dorada)",
            "global": True,
            "permanent": True
        }
    ],

    # Evento: Mensaje al mirar
    "event_scripts": {
        "on_look": {
            "after": [
                {
                    "script": "script_mensaje_ambiente(mensaje='Las manzanas brillan tentadoramente.')",
                    "priority": 1
                }
            ]
        }
    },

    "display": {
        "icon": "🌳"
    }
}
```

#### Ejemplo 2: Fuente Mágica (Eventos + Cooldowns)

```python
"fuente_magica_plaza": {
    "name": "una fuente mágica",
    "keywords": ["fuente", "magica", "fuente magica", "marmol"],
    "description": "Una magnífica fuente de mármol blanco. El agua cristalina brilla con un resplandor místico.",
    "category": "ambiente",
    "is_fixture": True,

    "locks": {
        "get": "rol(SUPERADMIN)"
    },
    "lock_messages": {
        "get": "La fuente es parte de la plaza. No puedes llevártela."
    },

    # Comando especial: /tirarmoneda fuente
    # (requeriría implementar comando nuevo o usar scripts)

    "display": {
        "icon": "⛲"
    }
}
```

#### Ejemplo 3: Palanca que Abre Puerta (Eventos + Estado)

```python
"palanca_secreta": {
    "name": "una palanca oxidada",
    "keywords": ["palanca", "oxidada", "palanca oxidada"],
    "description": "Una vieja palanca de hierro sobresale de la pared. Parece que se puede accionar.",
    "category": "ambiente",
    "is_fixture": True,

    "locks": {
        "get": "rol(SUPERADMIN)"
    },
    "lock_messages": {
        "get": "La palanca está firmemente empotrada en la pared."
    },

    # Comando especial: /accionar palanca
    # Script verifica estado y abre/cierra puerta

    "display": {
        "icon": "🔧"
    }
}
```

#### Ejemplo 4: Estatua para Rezar (Eventos + Cooldowns)

```python
"estatua_dios_guerra": {
    "name": "una estatua del dios de la guerra",
    "keywords": ["estatua", "dios", "guerra", "estatua del dios de la guerra"],
    "description": "Una imponente estatua de bronce representa al dios de la guerra en toda su gloria. Sus ojos parecen seguirte.",
    "category": "ambiente",
    "is_fixture": True,

    "locks": {
        "get": "rol(SUPERADMIN)"
    },
    "lock_messages": {
        "get": "La estatua pesa varias toneladas. Es imposible moverla."
    },

    # Evento ON_LOOK con cooldown
    "event_scripts": {
        "on_look": {
            "after": [
                {
                    "script": "script_rezar_estatua(buff=fuerza, duracion=300)",
                    "priority": 5
                }
            ]
        }
    },

    "display": {
        "icon": "🗿"
    }
}
```

---

### FASE 3: Documentación (Agente runegram-docs-keeper)

**Archivos a crear/actualizar**:

1. **`docs/creacion-de-contenido/objetos-de-ambiente.md`** (NUEVO)
   - Concepto de fixtures vs items regulares
   - Cuándo usar fixtures vs detalles de sala
   - Ejemplos completos con scripts
   - Mejores prácticas

2. **`docs/creacion-de-contenido/creacion-de-items.md`** (ACTUALIZAR)
   - Agregar sección sobre `is_fixture`
   - Explicar diferencia visual en sala
   - Enlazar a nueva documentación

3. **`docs/sistemas-del-motor/sistema-de-prototipos.md`** (ACTUALIZAR)
   - Agregar `is_fixture` a campos disponibles
   - Explicar comportamiento en templates

4. **`game_data/item_prototypes.py`** (ACTUALIZAR)
   - Agregar comentarios explicativos en ejemplos
   - Documentar estructura de fixture

---

### FASE 4: Migración y Testing

**No requiere migración de BD** ✅ (es solo una flag en prototipos)

**Testing manual**:
1. Crear sala con fixture de ejemplo
2. Verificar que aparece integrado en descripción
3. Verificar que NO aparece en "Cosas a la vista"
4. Probar `/mirar <fixture>` funciona
5. Probar `/coger <fixture>` muestra mensaje de lock
6. Probar scripts/eventos del fixture funcionan

---

## 📋 Comparativa: Fixtures vs Detalles vs Items

| Característica | Detalles (`details`) | Fixtures (`is_fixture: True`) | Items Regulares |
|----------------|---------------------|-------------------------------|-----------------|
| **Definición** | En prototipo de sala | En prototipo de item | En prototipo de item |
| **Persistencia BD** | ❌ No (solo texto) | ✅ Sí (instancia Item) | ✅ Sí (instancia Item) |
| **Visible en sala** | ❌ Solo con `/mirar` | ✅ Sí (integrado) | ✅ Sí (lista separada) |
| **Se puede coger** | ❌ No es objeto | ⚠️ Solo con locks | ✅ Por defecto sí |
| **Locks** | ❌ N/A | ✅ Sí (contextuales) | ✅ Sí (contextuales) |
| **Scripts/Eventos** | ❌ N/A | ✅ Sí (completos) | ✅ Sí (completos) |
| **Estado persistente** | ❌ N/A | ✅ Sí (`script_state`) | ✅ Sí (`script_state`) |
| **Scheduling** | ❌ N/A | ✅ Sí (tick + cron) | ✅ Sí (tick + cron) |
| **Caso de uso** | Atmosfera pura | Ambiente interactivo | Objetos portables |

**Regla de oro**:
- **Detalle**: Descripción inmersiva sin funcionalidad (una grieta, un cartel)
- **Fixture**: Objeto interactivo pero fijo (árbol frutal, palanca, fuente)
- **Item regular**: Objeto que puede moverse/cogerse (espada, poción, llave)

---

## 🚀 Plan de Ejecución

### Orden de Tareas

1. ✅ **Análisis completo** (COMPLETADO)
2. ⏳ **Extender `world_loader_service.py`** para sincronizar fixtures automáticamente
3. ⏳ **Modificar template** `room.html.j2` para separar fixtures visualmente
4. ⏳ **Crear 3-4 fixtures de ejemplo** en `item_prototypes.py`
5. ⏳ **Agregar campo `fixtures`** a salas en `room_prototypes.py`
6. ⏳ **Testing manual** en ambiente de desarrollo
7. ⏳ **Documentación completa** (agente runegram-docs-keeper)
8. ⏳ **Commit y push** con mensaje descriptivo

### Criterios de Éxito

✅ Fixtures definidos en `room_prototypes.py` se crean automáticamente al arrancar
✅ Fixtures aparecen integrados en descripción de sala
✅ Fixtures NO aparecen en "Cosas a la vista"
✅ `/mirar <fixture>` funciona correctamente
✅ Locks contextuales funcionan (no se pueden coger)
✅ Scripts y eventos del fixture se ejecutan
✅ Reiniciar bot NO duplica fixtures (idempotencia)
✅ Estado persistente de fixtures se preserva entre reinicios
✅ Documentación completa y clara
✅ Ejemplos listos para usar por creadores de contenido

---

## 📝 Notas de Implementación

### Consideraciones Técnicas

1. **Filtro Jinja2**: Usar `selectattr` y `rejectattr` para separar fixtures
2. **Performance**: No hay impacto (misma query, solo filtrado en template)
3. **Retrocompatibilidad**: 100% - items sin flag funcionan igual
4. **Extensibilidad**: Fixtures pueden tener CUALQUIER funcionalidad de items

### Decisiones de Diseño

1. **¿Por qué no usar `category="ambiente"`?**
   - Category es para organización/filtrado, no para comportamiento
   - Un fixture puede ser de categoría "mueble", "natural", "religioso", etc.

2. **¿Por qué no crear nuevo modelo `Fixture`?**
   - Código duplicado innecesario
   - Items ya tienen toda la funcionalidad necesaria
   - Separación complicaría queries y lógica

3. **¿Por qué mostrar fixtures antes de "Cosas a la vista"?**
   - Fixtures son parte del ambiente (como descripción)
   - Items regulares son transitorios
   - Mejor inmersión narrativa

### Futuras Extensiones (Opcionales)

1. **Comandos especializados para fixtures**:
   - `/accionar <fixture>` para palancas
   - `/tirarmoneda <fuente>` para fuentes mágicas
   - `/rezar <estatua>` para estatuas

2. **Fixtures con inventario**:
   - Un altar que contiene ofrendas
   - Un árbol hueco que guarda tesoros
   - (ya soportado con `is_container`)

3. **Fixtures que cambian de estado**:
   - Palanca arriba/abajo
   - Fuente con/sin agua
   - (ya soportado con `script_state`)

---

## 🎨 Ejemplo Visual Completo

### Antes (Sin Fixtures)

```
🏛️ PLAZA CENTRAL DE RUNEGARD
Estás en el corazón de la ciudad...

🔍 Cosas a la vista:
    1. 🌳 un árbol frutal
    2. ⛲ una fuente mágica
    3. 🗿 una estatua del dios de la guerra
    4. ⚔️ una espada oxidada
    5. 📜 un pergamino arrugado
```
❌ **Problema**: Fixtures mezclados con items regulares, no se diferencia el ambiente de objetos temporales

### Después (Con Fixtures)

```
🏛️ PLAZA CENTRAL DE RUNEGARD
Estás en el corazón de la ciudad. El bullicio de mercaderes...

🌳 Un árbol frutal
⛲ Una fuente mágica
🗿 Una estatua del dios de la guerra

🔍 Cosas a la vista:
    1. ⚔️ una espada oxidada
    2. 📜 un pergamino arrugado

👥 Personajes:
    - 🧙 Gandalf

🚪 Salidas:
    - ⬆️ Norte (Calle)
```
✅ **Mejora**: Separación clara entre ambiente permanente y objetos transitorios

---

**Última actualización:** 2025-10-18
**Autor:** Claude Code (Análisis y diseño de arquitectura)
**Estado:** ✅ Plan completo y listo para implementación
**Complejidad estimada:** BAJA (1-2 horas de desarrollo + testing)
**Impacto:** ALTO (mejora significativa de inmersión y usabilidad)
