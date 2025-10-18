---
título: "Escribiendo Scripts en Runegram"
categoría: "Creación de Contenido"
audiencia: "creador-de-contenido, desarrollador"
última_actualización: "2025-10-17"
autor: "Proyecto Runegram"
etiquetas: ["scripts", "prototipos", "eventos", "scheduling", "estado"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-scheduling.md"
  - "sistemas-del-motor/sistema-de-eventos.md"
  - "sistemas-del-motor/sistema-de-estado.md"
  - "sistemas-del-motor/sistema-de-scripts.md"
  - "creacion-de-contenido/creacion-de-items.md"
referencias_código:
  - "src/services/script_service.py"
  - "src/services/event_service.py"
  - "src/services/scheduler_service.py"
  - "src/services/state_service.py"
  - "game_data/item_prototypes.py"
estado: "actual"
importancia: "alta"
---

# Guía Práctica: Escribiendo Scripts

El **Sistema de Scripts** es lo que permite que el contenido del juego tenga comportamiento dinámico. Es el puente que conecta las definiciones de datos con la lógica del motor, dando vida a los objetos y al mundo.

## 🎯 Arquitectura

El sistema de scripts está compuesto por **4 servicios coordinados**:

1. **`script_service`**: Core del sistema (registro y ejecución de scripts)
2. **`event_service`**: Scripts **reactivos** (responden a eventos del juego)
3. **`scheduler_service`**: Scripts **proactivos** (ejecutan en intervalos de tiempo)
4. **`state_service`**: Gestión de estado persistente y transiente

Esta guía se divide en dos partes:
1. **Para Diseñadores de Contenido:** Cómo *usar* los scripts existentes en los prototipos.
2. **Para Desarrolladores del Motor:** Cómo *crear* nuevas funciones de script.

---

## 1. Para Diseñadores de Contenido: Usando Scripts

Como diseñador, no necesitas escribir código Python. Solo necesitas saber qué "habilidades" de script existen y cómo invocarlas desde los archivos de `game_data`.

Los scripts se invocan a través de `script strings`, que tienen un formato de llamada de función: `nombre_del_script(argumento=valor)`.

### 1.1. Scripts Reactivos (Eventos BEFORE/AFTER)

Los scripts de evento reaccionan a las acciones de los jugadores. Se ejecutan en dos fases:

- **BEFORE**: Antes de la acción (puede cancelarla)
- **AFTER**: Después de la acción (para efectos)

#### Formato con Prioridades (Recomendado)

```python
# En game_data/item_prototypes.py
"cofre_trampa": {
    "name": "un cofre de hierro",
    "description": "Un cofre cerrado con candado.",
    "event_scripts": {
        "on_get": {
            "before": [
                {
                    "script": "script_verificar_trampa",
                    "priority": 10  # Mayor prioridad = ejecuta primero
                }
            ],
            "after": [
                {
                    "script": "script_activar_trampa",
                    "priority": 5
                }
            ]
        }
    }
}
```

#### Formato Simple (Retrocompatible)

```python
"amuleto_antiguo": {
    "name": "un amuleto antiguo",
    "description": "Una joya opaca que parece absorber la luz.",
    "scripts": {
        "on_look": "script_notificar_brillo_magico(color=púrpura)"
    }
}
```

**Nota**: El formato simple se ejecuta automáticamente en la fase AFTER con prioridad 0.

#### Eventos Disponibles

- `on_look`: Cuando un jugador mira el objeto
- `on_get`: Cuando un jugador coge el objeto
- `on_drop`: Cuando un jugador suelta el objeto
- `on_put`: Cuando un jugador mete el objeto en un contenedor
- `on_take`: Cuando un jugador saca el objeto de un contenedor
- `on_use`: Cuando un jugador usa el objeto

#### Ejemplo: Cancelar Acción con BEFORE

```python
"espada_maldita": {
    "name": "una espada maldita",
    "description": "Una espada que emana energía oscura.",
    "event_scripts": {
        "on_get": {
            "before": [
                {
                    "script": "script_verificar_maldicion",  # Retorna False para cancelar
                    "priority": 10
                }
            ]
        }
    }
}
```

Si `script_verificar_maldicion` retorna `False`, el jugador NO podrá coger la espada.

### 1.2. Scripts Proactivos (Scheduling)

Los scheduling scripts hacen que el mundo actúe por sí solo, ejecutándose basándose en el tiempo.

#### Tick Scripts (Retrocompatible)

Basados en ticks del sistema (1 tick = 2 segundos por defecto).

```python
"craneo_susurrante": {
    "name": "un cráneo susurrante",
    "description": "Un cráneo amarillento que parece murmurar.",
    "tick_scripts": [
        {
            "interval_ticks": 150,  # Cada 300 segundos (150 * 2s)
            "script": "script_espada_susurra_secreto",
            "category": "ambient",  # Solo para jugadores online
            "permanent": True  # Se repite indefinidamente
        }
    ]
}
```

**Cálculo de `interval_ticks`:**
- 10 segundos → `10 / 2 = 5 ticks`
- 1 minuto → `60 / 2 = 30 ticks`
- 5 minutos → `300 / 2 = 150 ticks`
- 1 hora → `3600 / 2 = 1800 ticks`

#### Cron Scripts

Basados en expresiones cron (más precisos y flexibles).

```python
"campana_de_misa": {
    "name": "una campana de iglesia",
    "description": "Una gran campana de bronce.",
    "scheduled_scripts": [
        {
            "schedule": "0 12 * * *",  # Diario a las 12:00
            "script": "script_tocar_campanas",
            "global": True  # Una ejecución (no por jugador)
        },
        {
            "schedule": "0 18 * * *",  # Diario a las 18:00
            "script": "script_tocar_campanas",
            "global": True
        }
    ]
}
```

**Formato Cron**: `minuto hora día mes día_semana`
- `0 12 * * *` → Todos los días a las 12:00
- `*/15 * * * *` → Cada 15 minutos
- `0 0 * * 0` → Cada domingo a medianoche
- `0 9-17 * * 1-5` → De 9:00 a 17:00, de lunes a viernes

**Global vs Per-Player**:
- `"global": True` → Script se ejecuta UNA sola vez (ej: broadcast global)
- `"global": False` → Script se ejecuta para CADA jugador online con el objeto

### 1.3. Scripts con Estado

Los scripts pueden mantener estado entre ejecuciones usando `state_service`.

#### Estado Persistente (Sobrevive Reinicios)

```python
"pocion_de_tres_usos": {
    "name": "una poción de curación",
    "description": "Una poción que cura heridas. Tiene 3 usos.",
    "event_scripts": {
        "on_use": {
            "after": [
                {
                    "script": "script_usar_pocion_limitada(usos_max=3)",
                    "priority": 5
                }
            ]
        }
    }
}
```

El script puede usar:
```python
# Dentro del script
usos_restantes = await state_service.get_persistent(session, item, "usos_restantes", default=3)
await state_service.decrement_persistent(session, item, "usos_restantes", min_value=0)
await session.commit()

if usos_restantes <= 0:
    # Destruir item
    await delete_item(session, item)
```

#### Estado Transiente (Cooldowns con TTL)

```python
"anillo_teletransporte": {
    "name": "un anillo de teletransporte",
    "description": "Un anillo que permite teletransportarse.",
    "event_scripts": {
        "on_use": {
            "before": [
                {
                    "script": "script_verificar_cooldown_anillo",
                    "priority": 10
                }
            ],
            "after": [
                {
                    "script": "script_teletransportar_jugador(destino=plaza_central)",
                    "priority": 5
                }
            ]
        }
    }
}
```

El script puede usar:
```python
# Verificar cooldown (BEFORE)
if await state_service.is_on_cooldown(item, "uso_anillo"):
    segundos_restantes = await state_service.get_cooldown_remaining(item, "uso_anillo")
    await message.answer(f"Debes esperar {segundos_restantes:.0f} segundos.")
    return False  # Cancelar acción

# Establecer cooldown (AFTER)
await state_service.set_cooldown(item, "uso_anillo", timedelta(minutes=5))
```

### 1.4. Funciones de Script Disponibles

#### Scripts de Eventos
- `script_notificar_brillo_magico(color=...)`: Mensaje privado de brillo mágico

#### Scripts de Scheduling
- `script_espada_susurra_secreto()`: Envía susurro aleatorio a jugadores en sala

#### Scripts con Estado
- `script_usar_pocion_limitada(usos_max=...)`: Poción con usos limitados
- `script_verificar_cooldown(cooldown_key=..., cooldown_seconds=...)`: Verificar cooldown genérico

**Nota**: Para ver todas las funciones disponibles, consulta `src/services/script_service.py` o pregunta a un desarrollador.

---

## 2. Para Desarrolladores del Motor: Creando Nuevas Funciones de Script

Para expandir las capacidades del juego, los desarrolladores del motor pueden crear nuevas funciones de script.

**Archivo a editar:** `src/services/script_service.py`

### Paso 1: Escribir la Función de Lógica

Crea una nueva función `async` en la sección correspondiente del archivo. La función debe aceptar los parámetros del contexto.

#### Ejemplo 1: Script de Evento BEFORE (con Cancelación)

```python
# En src/services/script_service.py

async def script_verificar_nivel_minimo(
    session: AsyncSession,
    character: Character,
    target: Item,
    message: Message,
    nivel_requerido: int = 5,
    **kwargs
) -> bool:
    """
    Script BEFORE: Verifica que el personaje tenga nivel mínimo.
    Retorna False para cancelar la acción.

    Args:
        nivel_requerido: Nivel mínimo requerido (default: 5)
    """
    # (Lógica futura: cuando exista sistema de niveles)
    # nivel_actual = character.attributes.get("nivel", 1)

    # Simulación
    nivel_actual = 1

    if nivel_actual < nivel_requerido:
        await message.answer(
            f"❌ Necesitas nivel {nivel_requerido} para usar esto. "
            f"Tu nivel actual es {nivel_actual}."
        )
        return False  # Cancelar acción

    return True  # Permitir acción
```

#### Ejemplo 2: Script de Evento AFTER (con Efecto)

```python
async def script_curacion_menor(
    session: AsyncSession,
    character: Character,
    target: Item,
    message: Message,
    cantidad: int = 5,
    **kwargs
):
    """
    Script AFTER: Cura una pequeña cantidad de vida al personaje.

    Args:
        cantidad: Cantidad de vida a curar (default: 5)
    """
    # (Lógica futura: cuando el personaje tenga vida)
    # character.vida_actual = min(character.vida_actual + cantidad, character.vida_maxima)
    # await session.commit()

    # Por ahora, solo notificamos al jugador
    mensaje = f"✨ Sientes una oleada de energía restauradora emanando de {target.get_name()}."
    await message.answer(mensaje)
```

#### Ejemplo 3: Script de Scheduling (Cron)

```python
async def script_anuncio_automatico(
    session: AsyncSession,
    mensaje: str = "¡Servidor en mantenimiento en 1 hora!",
    **kwargs
):
    """
    Script CRON: Envía un anuncio automático a todos los jugadores online.

    Args:
        mensaje: Mensaje a enviar
    """
    from src.services import broadcaster_service

    # Obtener todos los jugadores online
    online_characters = await online_service.get_all_online_characters(session)

    for character in online_characters:
        await broadcaster_service.send_message_to_character(
            character,
            f"📢 <b>ANUNCIO DEL SERVIDOR</b>\n\n{mensaje}"
        )
```

#### Ejemplo 4: Script con Estado Persistente

```python
async def script_contar_usos(
    session: AsyncSession,
    character: Character,
    target: Item,
    message: Message,
    incremento: int = 1,
    **kwargs
):
    """
    Script: Cuenta cuántas veces se ha usado un objeto.

    Args:
        incremento: Cantidad a incrementar (default: 1)
    """
    from src.services import state_service

    # Incrementar contador
    usos_totales = await state_service.increment_persistent(
        session, target, "usos_totales", amount=incremento
    )
    await session.commit()

    await message.answer(f"Este objeto ha sido usado {usos_totales} veces.")
```

### Paso 2: Registrar la Nueva Función

Añade la función al diccionario `SCRIPT_REGISTRY`:

```python
# En src/services/script_service.py

SCRIPT_REGISTRY = {
    # Scripts existentes
    "script_notificar_brillo_magico": script_notificar_brillo_magico,
    "script_espada_susurra_secreto": script_espada_susurra_secreto,

    # --- NUEVOS SCRIPTS REGISTRADOS ---
    "script_verificar_nivel_minimo": script_verificar_nivel_minimo,
    "script_curacion_menor": script_curacion_menor,
    "script_anuncio_automatico": script_anuncio_automatico,
    "script_contar_usos": script_contar_usos,
}
```

### Paso 3: Documentar para Diseñadores

Actualiza esta documentación (sección 1.4) con la nueva función:

```markdown
#### Scripts de Validación
- `script_verificar_nivel_minimo(nivel_requerido=...)`: Verifica nivel mínimo (BEFORE)

#### Scripts de Curación
- `script_curacion_menor(cantidad=...)`: Cura vida al personaje (AFTER)

#### Scripts de Administración
- `script_anuncio_automatico(mensaje=...)`: Anuncio global (CRON)

#### Scripts de Tracking
- `script_contar_usos(incremento=...)`: Cuenta usos de un objeto (AFTER)
```

### Paso 4: Crear Prototipo de Ejemplo

Crea un prototipo en `game_data/item_prototypes.py` que use el nuevo script:

```python
"piedra_vital_premium": {
    "name": "una piedra de vitalidad premium",
    "description": "Una piedra suave y cálida al tacto. Solo para aventureros experimentados.",
    "event_scripts": {
        "on_use": {
            "before": [
                {
                    "script": "script_verificar_nivel_minimo(nivel_requerido=10)",
                    "priority": 10
                }
            ],
            "after": [
                {
                    "script": "script_curacion_menor(cantidad=20)",
                    "priority": 5
                },
                {
                    "script": "script_contar_usos",
                    "priority": 1
                }
            ]
        }
    }
}
```

---

## 3. Mejores Prácticas

### Para Diseñadores

1. **Usa formato con prioridades** para nuevos prototipos (más control y flexibilidad)
2. **Prioridades**: BEFORE scripts con prioridad alta (10+), AFTER con prioridad baja (1-5)
3. **Cron vs Tick**: Usa cron para eventos precisos (12:00), tick para intervalos variables
4. **Estado persistente**: Para contadores, progreso de quests, usos limitados
5. **Estado transiente**: Para cooldowns, buffs temporales, flags que expiran

### Para Desarrolladores

1. **SIEMPRE usa `async`**: Todo el código del motor es asíncrono
2. **Type hints**: Especifica tipos de parámetros y retorno
3. **Docstrings**: Documenta qué hace el script, qué argumentos acepta
4. **Logging**: Usa `logging.info()` para debugging
5. **Retorno de BEFORE**: `False` para cancelar, `True` para permitir (o `None`)
6. **Commit explícito**: Si modificas BD, haz `await session.commit()`
7. **Manejo de errores**: Usa `try/except` para operaciones críticas

### Seguridad

**⚠️ IMPORTANTE**: El sistema de scripts NO implementa sandboxing real. Solo ejecuta scripts confiables definidos en `game_data/` por desarrolladores autorizados.

**NO** permite:
- Ejecución de código arbitrario de jugadores
- Modificación de scripts en tiempo de ejecución
- Acceso a archivos del sistema
- Operaciones peligrosas (eval, exec, import dinámico)

---

## 4. Flujo de Desarrollo Completo

### Escenario: Agregar Objeto con Cooldown

**Objetivo**: Crear un "Elixir de Rapidez" que otorgue velocidad temporalmente, con cooldown de 10 minutos.

#### Paso 1: Diseñar el Script (Desarrollador)

```python
# En src/services/script_service.py

async def script_aplicar_buff_velocidad(
    session: AsyncSession,
    character: Character,
    target: Item,
    message: Message,
    duracion_segundos: int = 60,
    cooldown_minutos: int = 10,
    **kwargs
):
    """
    Aplica buff de velocidad temporal con cooldown.
    """
    from src.services import state_service
    from datetime import timedelta

    # Verificar cooldown
    if await state_service.is_on_cooldown(character, "buff_velocidad"):
        segundos = await state_service.get_cooldown_remaining(character, "buff_velocidad")
        await message.answer(f"⏱️ Debes esperar {segundos:.0f} segundos para usar otro elixir.")
        return

    # Aplicar buff (futuro: modificar stats del personaje)
    await message.answer(
        f"⚡ <b>¡Sientes una oleada de energía!</b>\n"
        f"Tu velocidad aumenta durante {duracion_segundos} segundos."
    )

    # Establecer cooldown
    await state_service.set_cooldown(
        character,
        "buff_velocidad",
        timedelta(minutes=cooldown_minutos)
    )

    # TODO: Agregar efecto temporal que expire después de duracion_segundos
    # (requiere sistema de buffs temporales)

# Registrar
SCRIPT_REGISTRY["script_aplicar_buff_velocidad"] = script_aplicar_buff_velocidad
```

#### Paso 2: Crear Prototipo (Diseñador)

```python
# En game_data/item_prototypes.py

"elixir_de_rapidez": {
    "name": "un elixir de rapidez",
    "description": "Un líquido plateado que parece moverse por sí solo dentro del frasco.",
    "category": "pocion",
    "tags": ["consumible", "temporal"],
    "event_scripts": {
        "on_use": {
            "after": [
                {
                    "script": "script_aplicar_buff_velocidad(duracion_segundos=60, cooldown_minutos=10)",
                    "priority": 5
                }
            ]
        }
    }
}
```

#### Paso 3: Generar el Objeto (Admin)

```
/generarobjeto elixir_de_rapidez
```

#### Paso 4: Probar (Jugador)

```
/coger elixir
/usar elixir
# Output: ⚡ ¡Sientes una oleada de energía! Tu velocidad aumenta durante 60 segundos.

/usar elixir
# Output: ⏱️ Debes esperar 600 segundos para usar otro elixir.
```

---

## 5. Recursos Adicionales

### Documentación Técnica
- [Sistema de Scripts](../sistemas-del-motor/sistema-de-scripts.md) - Arquitectura completa
- [Sistema de Eventos](../sistemas-del-motor/sistema-de-eventos.md) - Eventos BEFORE/AFTER
- [Sistema de Scheduling](../sistemas-del-motor/sistema-de-scheduling.md) - Tick y cron scripts
- [Sistema de Estado](../sistemas-del-motor/sistema-de-estado.md) - Estado persistente y transiente

### Código Fuente
- `src/services/script_service.py` - Core del sistema
- `src/services/event_service.py` - Gestión de eventos
- `src/services/scheduler_service.py` - Scheduling
- `src/services/state_service.py` - Gestión de estado

### Guías Relacionadas
- [Creación de Items](creacion-de-items.md) - Cómo crear prototipos de items
- [Construcción de Salas](construccion-de-salas.md) - Cómo crear salas con scripts

---

**Este ciclo de desarrollo (crear → registrar → usar) permite al motor crecer en capacidades sin mezclar su lógica con la definición del contenido.**
