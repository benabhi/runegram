# Análisis y Propuesta: Sistema de Scripts v2.0 para Runegram

**Fecha**: 2025-01-16
**Autor**: Claude (Análisis solicitado por Usuario)
**Estado**: Propuesta - Pendiente de Implementación

---

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis del Sistema Actual](#análisis-del-sistema-actual)
3. [Requisitos y Casos de Uso Solicitados](#requisitos-y-casos-de-uso-solicitados)
4. [Limitaciones del Sistema Actual](#limitaciones-del-sistema-actual)
5. [Propuesta de Arquitectura v2.0](#propuesta-de-arquitectura-v20)
6. [Componentes Detallados](#componentes-detallados)
7. [Plan de Implementación](#plan-de-implementación)
8. [Consideraciones de Performance](#consideraciones-de-performance)
9. [Migración y Retrocompatibilidad](#migración-y-retrocompatibilidad)
10. [Referencias y Recursos](#referencias-y-recursos)

---

## 📊 Resumen Ejecutivo

El sistema de scripts actual de Runegram es funcional pero limitado. Soporta:
- ✅ Scripts reactivos a eventos (`on_look`)
- ✅ Scripts proactivos basados en ticks (`tick_scripts`)
- ✅ Ejecución segura mediante registro de funciones

Sin embargo, carece de:
- ❌ Eventos hooks extensibles (solo `on_look` implementado)
- ❌ Programación temporal tipo cron (días/horas específicas)
- ❌ Scripts globales reutilizables en múltiples contextos
- ❌ Sistema de prioridades y dependencias entre scripts
- ❌ Gestión de estado persistente entre ejecuciones
- ❌ Soporte para scripts condicionales complejos

**Propuesta**: Sistema de Scripts v2.0 con arquitectura modular, scheduler avanzado, hooks extensibles, y scripts globales.

---

## 🔍 Análisis del Sistema Actual

### Arquitectura Actual

#### 1. **script_service.py** - Motor de Ejecución

**Componentes**:
- `SCRIPT_REGISTRY`: Dict que mapea nombres → funciones Python
- `_parse_script_string()`: Parser simple de argumentos `nombre(arg=val)`
- `execute_script()`: Ejecutor que busca en registry y ejecuta

**Características**:
```python
# Registro de scripts
SCRIPT_REGISTRY = {
    "script_notificar_brillo_magico": script_notificar_brillo_magico,
    "script_espada_susurra_secreto": script_espada_susurra_secreto,
}

# Ejecución
await execute_script(
    script_string="script_notificar_brillo_magico(color=rojo)",
    session=session,
    character=character,
    target=item
)
```

**Fortalezas**:
- ✅ Separación motor/contenido (filosofía core de Runegram)
- ✅ Seguro (no eval/exec, solo funciones registradas)
- ✅ Simple de entender y extender
- ✅ Manejo de errores robusto (no crashea el juego)

**Limitaciones**:
- ❌ Parser muy básico (solo `key=value`, no soporta strings con espacios, listas, etc.)
- ❌ Sin validación de argumentos
- ❌ Sin tipo de retorno documentado/validado
- ❌ Sin sistema de logging/debugging de scripts individuales

#### 2. **Scripts Reactivos (Event-Driven)**

**Implementación Actual**:
```python
# En prototipos
"espada_viviente": {
    "scripts": {
        "on_look": "script_notificar_brillo_magico(color=rojo)"
    }
}

# En comandos (ej: CmdLook)
if "on_look" in item_to_look.prototype.get("scripts", {}):
    await script_service.execute_script(
        script_string=item_to_look.prototype["scripts"]["on_look"],
        session=session,
        character=character,
        target=item_to_look
    )
```

**Eventos Actuales**:
- `on_look`: Único evento implementado (en CmdLook línea 74)

**Fortalezas**:
- ✅ Fácil de agregar nuevos hooks en comandos
- ✅ Contexto rico (character, target, session)

**Limitaciones**:
- ❌ Solo 1 evento implementado (`on_look`)
- ❌ Hardcodeado en cada comando (no centralizado)
- ❌ No hay prioridades (si múltiples scripts se disparan)
- ❌ No hay forma de cancelar/modificar la acción del comando
- ❌ No hay scripts "before" vs "after" (solo ejecuta después)

**Eventos Potenciales** (no implementados):
- `on_get`, `on_drop`, `on_put`, `on_take`
- `on_use`, `on_open`, `on_close`
- `on_enter_room`, `on_leave_room`
- `on_attack`, `on_defend`, `on_damage`
- `on_death`, `on_respawn`
- `on_say`, `on_whisper`
- `on_tick` (para entidades específicas, no global)

#### 3. **Scripts Proactivos (Tick-Based)**

**Implementación Actual** (`pulse_service.py`):
```python
# En prototipos
"espada_viviente": {
    "tick_scripts": [
        {
            "interval_ticks": 60,  # Cada 120s (60 * 2s)
            "script": "script_espada_susurra_secreto",
            "category": "ambient",
            "permanent": True  # Se repite
        }
    ]
}
```

**Flujo de Ejecución**:
1. Pulse global cada 2s incrementa `_global_tick_counter`
2. `_process_items_tick_scripts()` itera TODOS los Items
3. Para cada item, verifica si `current_tick - last_executed_tick >= interval_ticks`
4. Si es momento, ejecuta el script para cada personaje online en la sala
5. Actualiza `item.tick_data` con tracking

**Fortalezas**:
- ✅ Escalable (1 job vs N jobs)
- ✅ Sincronizado (todos en misma timeline)
- ✅ Simple para diseñadores ("60 ticks" vs cron)
- ✅ Soporta one-shot (`permanent: False`)
- ✅ Filtra por online (category ambient)

**Limitaciones**:
- ❌ Solo soporta intervalos fijos (no cron-like)
- ❌ No soporta días/horas específicas ("todos los lunes a las 10:00")
- ❌ Contador NO persiste (resetea al reiniciar bot)
- ❌ Solo Items tienen tick_scripts (Rooms no tienen)
- ❌ Performance O(n) con muchos items (itera todos)
- ❌ No hay gestión de prioridades/orden de ejecución
- ❌ No hay dependencias entre scripts

#### 4. **Tracking y Estado**

**Implementación Actual** (`item.tick_data` JSONB):
```python
item.tick_data = {
    "script_0": {
        "last_executed_tick": 58,
        "has_executed": True
    }
}
```

**Fortalezas**:
- ✅ Persiste en BD
- ✅ Por item, por script

**Limitaciones**:
- ❌ Solo almacena datos de timing, no estado custom
- ❌ No hay forma de que scripts guarden datos persistentes
- ❌ No hay logs de ejecución histórica

---

## 🎯 Requisitos y Casos de Uso Solicitados

### Requisito 1: Eventos Hooks Extensibles

**Caso de Uso**: Scripts que se ejecutan cuando se ejerce un comando sobre una entidad.

**Ejemplos**:
```python
# Item que brilla al ser mirado (ya existe)
"amuleto": {
    "scripts": {
        "on_look": "script_notificar_brillo_magico(color=azul)"
    }
}

# Puerta que se cierra sola al ser abierta
"puerta_trampa": {
    "scripts": {
        "on_open": "script_cerrar_tras_delay(segundos=5)",
        "on_close": "script_notificar_sala(mensaje=La puerta se cierra con un click ominoso)"
    }
}

# Item que no se puede coger (con script custom en vez de lock)
"piedra_maldita": {
    "scripts": {
        "on_get": "script_danar_personaje(cantidad=10)",  # Se puede coger pero hace daño
        "on_drop": "script_curar_personaje(cantidad=5)"    # Soltar cura
    }
}

# Room que ejecuta script al entrar
"sala_trampa": {
    "scripts": {
        "on_enter": "script_activar_trampa(tipo=flechas)",
        "on_leave": "script_notificar_escape"
    }
}
```

**Eventos Deseados**:
- **Items**: `on_look`, `on_get`, `on_drop`, `on_use`, `on_open`, `on_close`, `on_put`, `on_take`, `on_destroy`
- **Rooms**: `on_enter`, `on_leave`, `on_look`
- **Characters**: `on_death`, `on_respawn`, `on_login`, `on_logout`, `on_level_up`
- **Combat** (futuro): `on_attack`, `on_defend`, `on_damage`, `on_kill`, `on_die`

### Requisito 2: Programación Temporal Tipo Cron

**Caso de Uso**: Ejecutar scripts en días/horas específicas (calendario real).

**Ejemplos**:
```python
# Puerta que se abre los lunes a las 10:00 y se cierra los martes a las 10:00
"puerta_temporal": {
    "scheduled_scripts": [
        {
            "schedule": "0 10 * * MON",  # Cron: lunes 10:00
            "script": "script_abrir_puerta",
            "permanent": True
        },
        {
            "schedule": "0 10 * * TUE",  # Cron: martes 10:00
            "script": "script_cerrar_puerta",
            "permanent": True
        }
    ]
}

# Mercader que aparece solo los fines de semana
"mercader_errante": {
    "scheduled_scripts": [
        {
            "schedule": "0 8 * * SAT",  # Sábado 8:00
            "script": "script_spawn_npc(npc_id=mercader)",
            "permanent": True
        },
        {
            "schedule": "0 20 * * SUN",  # Domingo 20:00
            "script": "script_despawn_npc(npc_id=mercader)",
            "permanent": True
        }
    ]
}

# Evento global: Lluvia de meteoros cada noche a las 00:00
"mundo": {
    "scheduled_scripts": [
        {
            "schedule": "0 0 * * *",  # Diario medianoche
            "script": "script_evento_meteoros",
            "permanent": True,
            "global": True  # Se ejecuta una vez, no por jugador
        }
    ]
}
```

**Formato Cron** (estándar Unix):
```
* * * * *
│ │ │ │ └─ Día de la semana (0-6, 0=Domingo o MON-SUN)
│ │ │ └─── Mes (1-12 o JAN-DEC)
│ │ └───── Día del mes (1-31)
│ └─────── Hora (0-23)
└───────── Minuto (0-59)
```

### Requisito 3: Scripts Globales Reutilizables

**Caso de Uso**: Scripts que se pueden usar en diferentes contextos sin duplicar código.

**Ejemplos**:
```python
# Script global que puede ser usado por múltiples entidades
# En lugar de definir en prototipos, se define una vez y se referencia

# Definición en game_data/global_scripts.py
GLOBAL_SCRIPTS = {
    "danar_area": {
        "description": "Daña a todos los personajes en una sala",
        "parameters": {
            "cantidad": {"type": "int", "default": 10},
            "tipo": {"type": "str", "default": "fuego"}
        },
        "script": "script_danar_area"  # Función en script_service.py
    },
    "curar_area": {
        "description": "Cura a todos los personajes en una sala",
        "parameters": {
            "cantidad": {"type": "int", "default": 5}
        },
        "script": "script_curar_area"
    }
}

# Uso en múltiples prototipos
"volcan_activo": {
    "tick_scripts": [{
        "interval_ticks": 150,
        "global_script": "danar_area",  # Referencia al script global
        "args": {"cantidad": 20, "tipo": "lava"}
    }]
}

"trampa_fuego": {
    "scripts": {
        "on_enter": "global.danar_area(cantidad=15, tipo=fuego)"
    }
}

"fuente_curativa": {
    "tick_scripts": [{
        "interval_ticks": 60,
        "global_script": "curar_area",
        "args": {"cantidad": 5}
    }]
}
```

**Ventajas**:
- ✅ DRY (Don't Repeat Yourself)
- ✅ Mantenimiento centralizado
- ✅ Validación de parámetros consistente
- ✅ Documentación auto-generada para diseñadores

### Requisito 4: Estado Persistente Entre Ejecuciones

**Caso de Uso**: Scripts que necesitan recordar información entre ejecuciones.

**Ejemplos**:
```python
# Contador de visitantes a una sala
"sala_museo": {
    "scripts": {
        "on_enter": "script_contar_visitantes"  # Incrementa contador
    },
    "script_state": {
        "visitantes_totales": 0,
        "ultimo_visitante": null
    }
}

# Puerta que se puede abrir solo 3 veces
"puerta_fragil": {
    "scripts": {
        "on_open": "script_desgastar_puerta"
    },
    "script_state": {
        "usos_restantes": 3,
        "rota": false
    }
}

# Boss que recuerda quién lo atacó
"dragon_anciano": {
    "scripts": {
        "on_attack": "script_registrar_agresor"
    },
    "script_state": {
        "agresores": [],  # Lista de character_ids
        "primer_golpe": null  # character_id del primero que atacó
    }
}
```

---

## 🚫 Limitaciones del Sistema Actual

### 1. **Eventos Hardcodeados**

**Problema**: Solo `on_look` está implementado. Agregar nuevos eventos requiere modificar múltiples comandos.

**Ejemplo Actual** (CmdLook líneas 73-78):
```python
# Hardcodeado en cada comando
if "on_look" in item_to_look.prototype.get("scripts", {}):
    await script_service.execute_script(...)
```

**Consecuencia**: Agregar `on_get`, `on_drop`, etc. requiere modificar 10+ comandos manualmente.

### 2. **Sin Timing Calendario-Based**

**Problema**: No hay forma de ejecutar scripts en días/horas específicas del calendario real.

**Workaround Actual**: Calcular ticks manualmente (impráctico para fechas específicas).
```python
# ¿Cómo hacer "todos los lunes a las 10:00"?
# Imposible con sistema actual
```

### 3. **Sin Scripts Globales**

**Problema**: Cada prototipo debe definir su propio script, causando duplicación.

**Ejemplo**:
```python
# Duplicación en múltiples items
"trampa_fuego_1": {
    "scripts": {"on_enter": "script_danar_personaje(cantidad=10)"}
}
"trampa_fuego_2": {
    "scripts": {"on_enter": "script_danar_personaje(cantidad=10)"}
}
"trampa_fuego_3": {
    "scripts": {"on_enter": "script_danar_personaje(cantidad=10)"}
}
# Si queremos cambiar el daño, hay que modificar 3 lugares
```

### 4. **Sin Estado Persistente Custom**

**Problema**: Scripts no pueden guardar datos entre ejecuciones.

**Limitación Actual**: Solo `tick_data` para tracking de timing, no para estado custom.

### 5. **Parser Limitado**

**Problema**: Solo soporta `key=value`, no strings complejos, listas, etc.

**Ejemplos que NO funcionan**:
```python
# Strings con espacios
"on_enter": "script_mensaje(texto=Bienvenido a la sala)"  # ERROR

# Listas
"on_use": "script_teleport(destinos=[sala1, sala2, sala3])"  # ERROR

# Diccionarios
"on_look": "script_config(opciones={color: rojo, brillo: alto})"  # ERROR
```

### 6. **Sin Gestión de Prioridades**

**Problema**: Si múltiples scripts se disparan, no hay control sobre el orden.

**Ejemplo**:
```python
"item_complejo": {
    "scripts": {
        "on_get": "script_A",  # ¿Cuál se ejecuta primero?
        "on_get": "script_B"   # ¿O ambos? ¿En qué orden?
    }
}
```

### 7. **Sin Scripts "Before" / "After"**

**Problema**: Scripts solo se ejecutan después de la acción, no pueden prevenirla o modificarla.

**Caso de Uso Deseado**:
```python
# Prevenir acción si el script retorna False
"item_protegido": {
    "scripts": {
        "before_get": "script_verificar_permiso",  # Si retorna False, cancela /coger
        "after_get": "script_notificar_robo"       # Solo si el get tuvo éxito
    }
}
```

### 8. **Performance O(n) en Pulse**

**Problema**: `_process_items_tick_scripts()` itera TODOS los items en CADA tick.

**Código Actual** (pulse_service.py líneas 134-143):
```python
# Ineficiente con 10,000+ items
result = await session.execute(select(Item).options(...))
all_items = result.scalars().all()  # TODOS los items

for item in all_items:  # O(n) cada tick
    tick_scripts = item.prototype.get("tick_scripts", [])
    if not tick_scripts:
        continue  # Desperdicio: itera items sin scripts
```

**Optimización Deseada**: Solo cargar items CON tick_scripts.

---

## 🏗️ Propuesta de Arquitectura v2.0

### Visión General

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA DE APLICACIÓN                           │
│  (Comandos, Handlers, Lógica de Juego)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SCRIPT ENGINE v2.0                             │
│                                                                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Event Hub  │  │  Scheduler   │  │  Global Scripts Mgr  │  │
│  │  (Hooks)    │  │  (Cron+Tick) │  │  (Registry+Context)  │  │
│  └─────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │         Script Executor (Enhanced Parser + Runner)      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │         State Manager (Persistent + Transient)          │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PERSISTENCE LAYER                              │
│  (PostgreSQL, Redis, SCRIPT_REGISTRY)                          │
└─────────────────────────────────────────────────────────────────┘
```

### Filosofía de Diseño

1. **Mantener separación Motor/Contenido**: Scripts siguen siendo strings en prototipos
2. **Retrocompatibilidad total**: Scripts v1.0 siguen funcionando sin modificar
3. **Opt-in progresivo**: Nuevas features son opcionales
4. **Performance first**: Optimizaciones que escalan a 100k+ entidades
5. **Developer Experience**: Fácil agregar nuevos eventos y scripts
6. **Type Safety**: Validación de parámetros en tiempo de diseño

---

## 🔧 Componentes Detallados

### Componente 1: Event Hub (Sistema de Hooks Centralizado)

**Objetivo**: Centralizar el manejo de eventos para que comandos no tengan que hardcodear lógica de scripts.

#### 1.1 Diseño

**Archivo**: `src/services/event_hub.py`

```python
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass
import logging
from sqlalchemy.ext.asyncio import AsyncSession

# Definición de eventos soportados
class EventType(Enum):
    # Items
    ON_LOOK = "on_look"
    ON_GET = "on_get"
    ON_DROP = "on_drop"
    ON_USE = "on_use"
    ON_OPEN = "on_open"
    ON_CLOSE = "on_close"
    ON_PUT = "on_put"
    ON_TAKE = "on_take"
    ON_DESTROY = "on_destroy"

    # Rooms
    ON_ENTER = "on_enter"
    ON_LEAVE = "on_leave"
    ON_ROOM_LOOK = "on_room_look"

    # Characters
    ON_LOGIN = "on_login"
    ON_LOGOUT = "on_logout"
    ON_DEATH = "on_death"
    ON_RESPAWN = "on_respawn"
    ON_LEVEL_UP = "on_level_up"

    # Combat (futuro)
    ON_ATTACK = "on_attack"
    ON_DEFEND = "on_defend"
    ON_DAMAGE = "on_damage"
    ON_KILL = "on_kill"
    ON_DIE = "on_die"

# Fases de ejecución de eventos
class EventPhase(Enum):
    BEFORE = "before"  # Puede cancelar la acción
    AFTER = "after"    # Ejecuta después de la acción

@dataclass
class EventContext:
    """Contexto completo de un evento."""
    session: AsyncSession
    character: Optional[Any]  # Character que dispara el evento
    target: Optional[Any]      # Entidad objetivo (Item, Room, etc.)
    room: Optional[Any]        # Room donde ocurre
    extra: Dict[str, Any]      # Datos adicionales

@dataclass
class EventResult:
    """Resultado de ejecutar un evento."""
    success: bool              # ¿El evento se ejecutó correctamente?
    cancel_action: bool = False  # ¿Cancelar la acción original? (solo BEFORE)
    message: Optional[str] = None  # Mensaje opcional para el jugador
    data: Dict[str, Any] = None    # Datos adicionales

class EventHub:
    """
    Hub centralizado para manejo de eventos.

    Permite que los comandos disparen eventos sin conocer
    qué scripts existen.
    """

    def __init__(self):
        # Hooks globales: funciones que escuchan TODOS los eventos de un tipo
        self._global_hooks: Dict[EventType, List[Callable]] = {}

    async def trigger_event(
        self,
        event_type: EventType,
        phase: EventPhase,
        context: EventContext
    ) -> EventResult:
        """
        Dispara un evento y ejecuta todos los scripts asociados.

        Args:
            event_type: Tipo de evento (ON_GET, ON_LOOK, etc.)
            phase: Fase del evento (BEFORE o AFTER)
            context: Contexto completo del evento

        Returns:
            EventResult con el resultado de la ejecución
        """
        # Construir nombre del evento con fase
        event_name = f"{phase.value}_{event_type.value}"

        # 1. Ejecutar hooks globales (si existen)
        await self._execute_global_hooks(event_type, phase, context)

        # 2. Ejecutar scripts de la entidad objetivo
        if context.target:
            result = await self._execute_entity_scripts(
                entity=context.target,
                event_name=event_name,
                context=context,
                phase=phase
            )

            if phase == EventPhase.BEFORE and result.cancel_action:
                return result

        return EventResult(success=True)

    async def _execute_entity_scripts(
        self,
        entity: Any,
        event_name: str,
        context: EventContext,
        phase: EventPhase
    ) -> EventResult:
        """
        Ejecuta los scripts definidos en el prototipo de una entidad.
        """
        from src.services import script_service

        # Obtener prototipo
        if not hasattr(entity, 'prototype'):
            return EventResult(success=True)

        prototype = entity.prototype
        scripts = prototype.get("scripts", {})

        # Buscar script para este evento
        script_string = scripts.get(event_name)

        if not script_string:
            return EventResult(success=True)

        # Ejecutar el script
        try:
            result = await script_service.execute_script(
                script_string=script_string,
                session=context.session,
                character=context.character,
                target=context.target,
                room=context.room,
                **context.extra
            )

            # Procesar resultado del script
            if phase == EventPhase.BEFORE and result is False:
                # Script retornó False en fase BEFORE = cancelar acción
                return EventResult(
                    success=True,
                    cancel_action=True,
                    message="La acción fue cancelada."
                )

            return EventResult(success=True)

        except Exception:
            logging.exception(f"Error ejecutando script de evento {event_name}")
            return EventResult(success=False)

    async def _execute_global_hooks(
        self,
        event_type: EventType,
        phase: EventPhase,
        context: EventContext
    ):
        """Ejecuta hooks globales registrados para este tipo de evento."""
        hooks = self._global_hooks.get(event_type, [])

        for hook_func in hooks:
            try:
                await hook_func(phase, context)
            except Exception:
                logging.exception(f"Error en hook global para {event_type}")

    def register_global_hook(
        self,
        event_type: EventType,
        hook_func: Callable
    ):
        """
        Registra un hook global que escucha todos los eventos de un tipo.

        Útil para sistemas del motor que necesitan reaccionar a eventos
        (ej: sistema de combate, logging, achievements, etc.)
        """
        if event_type not in self._global_hooks:
            self._global_hooks[event_type] = []

        self._global_hooks[event_type].append(hook_func)


# Instancia singleton
event_hub = EventHub()
```

#### 1.2 Uso en Comandos

**Antes (v1.0 - Hardcodeado)**:
```python
# commands/player/general.py - CmdLook
class CmdLook(Command):
    async def execute(self, character, session, message, args):
        # ... lógica de mirar ...

        # Hardcodeado: verificar script on_look
        if "on_look" in item_to_look.prototype.get("scripts", {}):
            await script_service.execute_script(
                script_string=item_to_look.prototype["scripts"]["on_look"],
                session=session,
                character=character,
                target=item_to_look
            )
```

**Después (v2.0 - Con Event Hub)**:
```python
# commands/player/general.py - CmdLook
from src.services.event_hub import event_hub, EventType, EventPhase, EventContext

class CmdLook(Command):
    async def execute(self, character, session, message, args):
        # ... lógica de mirar ...

        # Disparar evento centralizado
        context = EventContext(
            session=session,
            character=character,
            target=item_to_look,
            room=character.room,
            extra={}
        )

        await event_hub.trigger_event(
            event_type=EventType.ON_LOOK,
            phase=EventPhase.AFTER,
            context=context
        )
```

#### 1.3 Uso en Prototipos

```python
# game_data/item_prototypes.py
"espada_viviente": {
    "scripts": {
        # v1.0 (backward compatible)
        "on_look": "script_notificar_brillo_magico(color=rojo)",

        # v2.0 (nuevas features)
        "before_get": "script_verificar_digno",  # Puede cancelar
        "after_get": "script_vincular_alma",     # Solo si get tuvo éxito
        "before_drop": "script_advertir_maldicion",
        "after_drop": "script_liberar_alma"
    }
}
```

#### 1.4 Ventajas

✅ **Centralización**: Un solo lugar para toda la lógica de eventos
✅ **Extensibilidad**: Agregar nuevo evento = agregar a enum + usar en comando
✅ **Hooks globales**: Sistemas del motor pueden reaccionar a eventos
✅ **Before/After phases**: Control fino sobre timing de ejecución
✅ **Cancelación**: Scripts pueden prevenir acciones (útil para validaciones custom)

---

### Componente 2: Enhanced Scheduler (Tick + Cron Híbrido)

**Objetivo**: Combinar el sistema de ticks actual con scheduling tipo cron para eventos calendario.

#### 2.1 Diseño

**Archivo**: `src/services/enhanced_scheduler.py`

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from croniter import croniter
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Item, Room
from src.services import script_service
from src.db import async_session_factory


class ScheduledScriptType(Enum):
    TICK = "tick"        # Intervalo de ticks (sistema actual)
    CRON = "cron"        # Expresión cron (nuevo)
    TIMESTAMP = "timestamp"  # Fecha/hora específica (nuevo)


@dataclass
class ScheduledScript:
    """Definición de un script programado."""
    script_string: str
    schedule_type: ScheduledScriptType

    # Para TICK
    interval_ticks: Optional[int] = None

    # Para CRON
    cron_expression: Optional[str] = None

    # Para TIMESTAMP
    execute_at: Optional[datetime] = None

    # Comunes
    permanent: bool = True
    category: str = "ambient"
    is_global: bool = False  # True = ejecuta una sola vez, False = por jugador
    priority: int = 0  # Mayor número = mayor prioridad


class EnhancedScheduler:
    """
    Scheduler híbrido que soporta:
    - Tick-based scheduling (sistema actual)
    - Cron-based scheduling (calendario)
    - Timestamp scheduling (eventos únicos)
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._tick_counter = 0

        # Cache de scripts cron (para evitar recargar prototipos cada tick)
        self._cron_scripts_cache: Dict[str, List[ScheduledScript]] = {}

    def start(self):
        """Inicializa el scheduler con todos sus jobs."""
        # Job 1: Pulse global (tick-based scripts)
        self.scheduler.add_job(
            self._execute_tick_pulse,
            trigger=IntervalTrigger(seconds=2),
            id='tick_pulse',
            replace_existing=True
        )

        # Job 2: Procesar scripts cron
        self.scheduler.add_job(
            self._process_cron_scripts,
            trigger=IntervalTrigger(minutes=1),  # Verificar cada minuto
            id='cron_processor',
            replace_existing=True
        )

        # Job 3: Cargar scripts cron desde prototipos
        self.scheduler.add_job(
            self._reload_cron_scripts,
            trigger=IntervalTrigger(minutes=5),  # Recargar cada 5 min
            id='cron_reload',
            replace_existing=True
        )

        self.scheduler.start()
        logging.info("Enhanced Scheduler iniciado.")

    async def _execute_tick_pulse(self):
        """
        Pulse global de ticks (mantiene comportamiento v1.0).
        """
        self._tick_counter += 1
        current_tick = self._tick_counter

        if current_tick % 30 == 0:
            logging.debug(f"Tick #{current_tick}")

        async with async_session_factory() as session:
            await self._process_tick_scripts(session, current_tick)

    async def _process_tick_scripts(self, session: AsyncSession, current_tick: int):
        """
        Procesa tick_scripts (sistema v1.0 - sin cambios).

        OPTIMIZACIÓN: Solo cargar items que tienen tick_scripts.
        """
        # Optimización: Filtrar items CON tick_scripts
        # Requiere agregar columna has_tick_scripts (boolean) o usar query JSON
        query = select(Item).where(
            Item.prototype['tick_scripts'].astext != None
        ).options(
            selectinload(Item.room),
            selectinload(Item.character)
        )

        result = await session.execute(query)
        items_with_scripts = result.scalars().all()

        for item in items_with_scripts:
            tick_scripts = item.prototype.get("tick_scripts", [])

            for idx, tick_script in enumerate(tick_scripts):
                await self._process_single_tick_script(
                    session=session,
                    item=item,
                    tick_script=tick_script,
                    script_index=idx,
                    current_tick=current_tick
                )

        await session.commit()

    async def _process_single_tick_script(
        self,
        session: AsyncSession,
        item: Item,
        tick_script: dict,
        script_index: int,
        current_tick: int
    ):
        """Procesa un tick_script individual (igual que v1.0)."""
        # ... (código actual de pulse_service.py sin cambios)
        pass

    async def _reload_cron_scripts(self):
        """
        Recarga todos los cron scripts desde prototipos.

        Esto permite que diseñadores agreguen nuevos cron scripts
        sin reiniciar el bot.
        """
        async with async_session_factory() as session:
            # Cargar items con scheduled_scripts
            query = select(Item).where(
                Item.prototype['scheduled_scripts'].astext != None
            )
            result = await session.execute(query)
            items = result.scalars().all()

            new_cache = {}

            for item in items:
                scheduled_scripts = item.prototype.get("scheduled_scripts", [])

                for script_def in scheduled_scripts:
                    if "schedule" in script_def:
                        # Es un cron script
                        cron_expr = script_def["schedule"]

                        scheduled_script = ScheduledScript(
                            script_string=script_def["script"],
                            schedule_type=ScheduledScriptType.CRON,
                            cron_expression=cron_expr,
                            permanent=script_def.get("permanent", True),
                            is_global=script_def.get("global", False),
                            category=script_def.get("category", "ambient")
                        )

                        # Agregar al cache por entity_id
                        entity_key = f"item_{item.id}"
                        if entity_key not in new_cache:
                            new_cache[entity_key] = []
                        new_cache[entity_key].append(scheduled_script)

            # Cargar rooms con scheduled_scripts (futuro)
            # ... similar al de items

            self._cron_scripts_cache = new_cache
            logging.info(f"Cron scripts cache actualizado: {len(new_cache)} entidades.")

    async def _process_cron_scripts(self):
        """
        Procesa todos los cron scripts que deben ejecutarse en este minuto.

        Se ejecuta cada minuto (job configurado en start).
        """
        now = datetime.now(timezone.utc)

        async with async_session_factory() as session:
            for entity_key, scheduled_scripts in self._cron_scripts_cache.items():
                for script in scheduled_scripts:
                    if self._should_execute_cron(script, now):
                        await self._execute_cron_script(session, entity_key, script, now)

    def _should_execute_cron(self, script: ScheduledScript, now: datetime) -> bool:
        """
        Verifica si un cron script debe ejecutarse en este momento.

        Usa croniter para parsing de expresiones cron.
        """
        try:
            cron = croniter(script.cron_expression, now)
            next_run = cron.get_prev(datetime)

            # Verificar si el script debió ejecutarse en el último minuto
            time_diff = (now - next_run).total_seconds()

            # Si la diferencia es menor a 60s, debe ejecutarse
            return 0 <= time_diff < 60

        except Exception:
            logging.exception(f"Error parsing cron: {script.cron_expression}")
            return False

    async def _execute_cron_script(
        self,
        session: AsyncSession,
        entity_key: str,
        script: ScheduledScript,
        execution_time: datetime
    ):
        """
        Ejecuta un cron script.

        Maneja scripts globales vs. por jugador.
        """
        # Parsear entity_key (ej: "item_123")
        entity_type, entity_id = entity_key.split("_")
        entity_id = int(entity_id)

        # Cargar entidad
        if entity_type == "item":
            entity = await session.get(Item, entity_id, options=[
                selectinload(Item.room),
                selectinload(Item.character)
            ])
        elif entity_type == "room":
            entity = await session.get(Room, entity_id)
        else:
            logging.warning(f"Tipo de entidad desconocido: {entity_type}")
            return

        if not entity:
            logging.warning(f"Entidad no encontrada: {entity_key}")
            return

        # Determinar contexto
        if script.is_global:
            # Script global: ejecutar una sola vez
            await script_service.execute_script(
                script_string=script.script_string,
                session=session,
                target=entity,
                room=getattr(entity, 'room', entity),
                execution_time=execution_time
            )
        else:
            # Script por jugador: ejecutar para cada jugador online en la sala
            room = getattr(entity, 'room', None) if hasattr(entity, 'room') else entity

            if not room:
                return

            # Obtener personajes online en la sala
            from src.services import online_service, player_service

            char_ids_query = select(Character.id).where(Character.room_id == room.id)
            result = await session.execute(char_ids_query)
            char_ids = result.scalars().all()

            for char_id in char_ids:
                if script.category == "ambient":
                    is_online = await online_service.is_character_online(char_id)
                    if not is_online:
                        continue

                character = await player_service.get_character_with_relations_by_id(
                    session, char_id
                )

                if not character:
                    continue

                await script_service.execute_script(
                    script_string=script.script_string,
                    session=session,
                    target=entity,
                    room=room,
                    character=character,
                    execution_time=execution_time
                )


# Instancia singleton
enhanced_scheduler = EnhancedScheduler()
```

#### 2.2 Uso en Prototipos

```python
# game_data/item_prototypes.py

"puerta_temporal": {
    "name": "una puerta mística",
    "description": "Una puerta que solo se abre en ciertos momentos.",
    "scheduled_scripts": [
        # Sistema v1.0 (tick-based) - sigue funcionando
        {
            "interval_ticks": 60,
            "script": "script_susurro_misterioso",
            "category": "ambient",
            "permanent": True
        },

        # Sistema v2.0 (cron-based) - NUEVO
        {
            "schedule": "0 10 * * MON",  # Lunes 10:00
            "script": "script_abrir_puerta",
            "permanent": True,
            "global": True  # Solo ejecuta una vez, no por jugador
        },
        {
            "schedule": "0 10 * * TUE",  # Martes 10:00
            "script": "script_cerrar_puerta",
            "permanent": True,
            "global": True
        }
    ]
}

"mercader_errante": {
    "name": "un mercader misterioso",
    "scheduled_scripts": [
        {
            "schedule": "0 8 * * SAT",  # Sábado 8:00 AM
            "script": "script_spawn_npc(npc_id=mercader_errante)",
            "permanent": True,
            "global": True
        },
        {
            "schedule": "0 20 * * SUN",  # Domingo 8:00 PM
            "script": "script_despawn_npc(npc_id=mercader_errante)",
            "permanent": True,
            "global": True
        }
    ]
}
```

#### 2.3 Ventajas

✅ **Calendario real**: Eventos vinculados a días/horas específicas
✅ **Flexible**: Combina ticks (simples) con cron (complejos)
✅ **Retrocompatible**: tick_scripts siguen funcionando igual
✅ **Scripts globales**: `global: True` ejecuta una vez en lugar de por jugador
✅ **Performance**: Cache de cron scripts, solo recarga cada 5 min

---

### Componente 3: Global Scripts Manager

**Objetivo**: Scripts reutilizables con validación de parámetros y documentación.

#### 3.1 Diseño

**Archivo**: `game_data/global_scripts.py`

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ParamType(Enum):
    """Tipos de parámetros soportados."""
    INT = "int"
    STR = "str"
    BOOL = "bool"
    FLOAT = "float"
    LIST = "list"
    DICT = "dict"


@dataclass
class ScriptParameter:
    """Definición de un parámetro de script."""
    name: str
    type: ParamType
    default: Any = None
    required: bool = False
    description: str = ""

    # Validaciones opcionales
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    allowed_values: Optional[list] = None


@dataclass
class GlobalScriptDefinition:
    """Definición completa de un script global."""
    key: str  # Identificador único
    name: str  # Nombre legible
    description: str
    script_function: str  # Nombre de la función en SCRIPT_REGISTRY
    parameters: Dict[str, ScriptParameter]
    category: str = "general"
    examples: list = None


# Catálogo de scripts globales
GLOBAL_SCRIPTS: Dict[str, GlobalScriptDefinition] = {
    "danar_area": GlobalScriptDefinition(
        key="danar_area",
        name="Dañar Área",
        description="Daña a todos los personajes en una sala.",
        script_function="script_danar_area",
        category="combat",
        parameters={
            "cantidad": ScriptParameter(
                name="cantidad",
                type=ParamType.INT,
                default=10,
                required=False,
                description="Cantidad de daño a infligir",
                min_value=1,
                max_value=100
            ),
            "tipo": ScriptParameter(
                name="tipo",
                type=ParamType.STR,
                default="fuego",
                required=False,
                description="Tipo de daño (fuego, hielo, etc.)",
                allowed_values=["fuego", "hielo", "veneno", "electrico"]
            ),
            "mensaje": ScriptParameter(
                name="mensaje",
                type=ParamType.STR,
                default="Una ola de {tipo} te golpea.",
                required=False,
                description="Mensaje personalizado para el jugador"
            )
        },
        examples=[
            "global.danar_area(cantidad=15, tipo=fuego)",
            "global.danar_area(cantidad=20, tipo=veneno, mensaje=El veneno te quema)"
        ]
    ),

    "curar_area": GlobalScriptDefinition(
        key="curar_area",
        name="Curar Área",
        description="Cura a todos los personajes en una sala.",
        script_function="script_curar_area",
        category="healing",
        parameters={
            "cantidad": ScriptParameter(
                name="cantidad",
                type=ParamType.INT,
                default=5,
                required=False,
                description="Cantidad de puntos a curar",
                min_value=1,
                max_value=50
            )
        },
        examples=[
            "global.curar_area(cantidad=10)"
        ]
    ),

    "teleport_aleatorio": GlobalScriptDefinition(
        key="teleport_aleatorio",
        name="Teletransporte Aleatorio",
        description="Teletransporta al personaje a una sala aleatoria que cumpla ciertos criterios.",
        script_function="script_teleport_aleatorio",
        category="movement",
        parameters={
            "categoria": ScriptParameter(
                name="categoria",
                type=ParamType.STR,
                default=None,
                required=False,
                description="Categoría de sala destino (opcional)"
            ),
            "tag": ScriptParameter(
                name="tag",
                type=ParamType.STR,
                default=None,
                required=False,
                description="Tag que debe tener la sala destino (opcional)"
            ),
            "excluir_actual": ScriptParameter(
                name="excluir_actual",
                type=ParamType.BOOL,
                default=True,
                required=False,
                description="No permitir teletransporte a la sala actual"
            )
        },
        examples=[
            "global.teleport_aleatorio()",
            "global.teleport_aleatorio(categoria=ciudad_runegard)",
            "global.teleport_aleatorio(tag=seguro, excluir_actual=true)"
        ]
    ),

    "spawn_item": GlobalScriptDefinition(
        key="spawn_item",
        name="Generar Item",
        description="Genera un nuevo item en la sala o inventario.",
        script_function="script_spawn_item",
        category="spawning",
        parameters={
            "item_key": ScriptParameter(
                name="item_key",
                type=ParamType.STR,
                required=True,
                description="Clave del prototipo de item a generar"
            ),
            "destino": ScriptParameter(
                name="destino",
                type=ParamType.STR,
                default="sala",
                required=False,
                description="Dónde aparece: 'sala' o 'inventario'",
                allowed_values=["sala", "inventario"]
            ),
            "cantidad": ScriptParameter(
                name="cantidad",
                type=ParamType.INT,
                default=1,
                required=False,
                description="Cantidad de items a generar",
                min_value=1,
                max_value=100
            )
        },
        examples=[
            "global.spawn_item(item_key=espada_herrumbrosa)",
            "global.spawn_item(item_key=pocion_curacion, destino=inventario, cantidad=3)"
        ]
    )
}


def get_global_script(key: str) -> Optional[GlobalScriptDefinition]:
    """Obtiene la definición de un script global por su clave."""
    return GLOBAL_SCRIPTS.get(key)


def list_global_scripts(category: Optional[str] = None) -> Dict[str, GlobalScriptDefinition]:
    """
    Lista todos los scripts globales, opcionalmente filtrados por categoría.

    Útil para comandos de admin que muestren scripts disponibles.
    """
    if category:
        return {
            key: script
            for key, script in GLOBAL_SCRIPTS.items()
            if script.category == category
        }
    return GLOBAL_SCRIPTS


def validate_script_parameters(
    script_key: str,
    provided_params: Dict[str, Any]
) -> tuple[bool, Optional[str]]:
    """
    Valida que los parámetros proporcionados sean correctos.

    Returns:
        (is_valid, error_message)
    """
    script_def = get_global_script(script_key)

    if not script_def:
        return False, f"Script global '{script_key}' no existe."

    # Verificar parámetros requeridos
    for param_name, param_def in script_def.parameters.items():
        if param_def.required and param_name not in provided_params:
            return False, f"Parámetro requerido '{param_name}' no proporcionado."

    # Validar tipos y rangos
    for param_name, param_value in provided_params.items():
        if param_name not in script_def.parameters:
            return False, f"Parámetro desconocido '{param_name}'."

        param_def = script_def.parameters[param_name]

        # Validar tipo (simplificado)
        if param_def.type == ParamType.INT:
            try:
                int_val = int(param_value)
                if param_def.min_value and int_val < param_def.min_value:
                    return False, f"{param_name} debe ser >= {param_def.min_value}"
                if param_def.max_value and int_val > param_def.max_value:
                    return False, f"{param_name} debe ser <= {param_def.max_value}"
            except ValueError:
                return False, f"{param_name} debe ser un número entero."

        # Validar valores permitidos
        if param_def.allowed_values and param_value not in param_def.allowed_values:
            return False, f"{param_name} debe ser uno de: {', '.join(param_def.allowed_values)}"

    return True, None
```

#### 3.2 Actualización de script_service.py

```python
# src/services/script_service.py

# Agregar importación
from game_data.global_scripts import get_global_script, validate_script_parameters

def _parse_script_string(script_string: str) -> tuple[str, dict, bool]:
    """
    Parser mejorado que soporta scripts globales.

    Returns:
        (script_name, kwargs, is_global_script)
    """
    # Detectar si es global script
    is_global = script_string.startswith("global.")

    if is_global:
        # Quitar prefijo "global."
        script_string = script_string[7:]

    # Parser existente
    match = re.match(r"(\w+)\((.*)\)", script_string)
    if not match:
        return script_string, {}, is_global

    name, args_str = match.groups()
    kwargs = {}

    if args_str:
        # Parser mejorado (soporta strings con espacios usando comillas)
        kwargs = _parse_advanced_arguments(args_str)

    return name, kwargs, is_global


def _parse_advanced_arguments(args_str: str) -> dict:
    """
    Parser avanzado de argumentos que soporta:
    - Strings con espacios: mensaje="Hola mundo"
    - Valores booleanos: activo=true
    - Números: cantidad=10
    - Listas simples: items=[espada, escudo]
    """
    import shlex

    kwargs = {}

    # Usar shlex para parsing avanzado
    try:
        # Preparar string para shlex (reemplazar = por espacio temporalmente)
        parts = shlex.split(args_str.replace('=', ' = '))

        i = 0
        while i < len(parts):
            if i + 2 < len(parts) and parts[i + 1] == '=':
                key = parts[i]
                value = parts[i + 2]

                # Convertir tipos
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit():
                    value = float(value)
                elif value.startswith('[') and value.endswith(']'):
                    # Lista simple
                    value = [v.strip() for v in value[1:-1].split(',')]

                kwargs[key] = value
                i += 3
            else:
                i += 1

    except Exception:
        logging.warning(f"Error parsing argumentos avanzados: {args_str}")
        # Fallback al parser simple
        try:
            kwargs = dict(arg.strip().split('=') for arg in args_str.split(','))
        except ValueError:
            pass

    return kwargs


async def execute_script(script_string: str, session: AsyncSession, **context):
    """
    Ejecutor mejorado que soporta scripts globales.
    """
    if not script_string:
        return

    script_name, kwargs, is_global = _parse_script_string(script_string)

    if is_global:
        # Validar parámetros contra definición
        is_valid, error_msg = validate_script_parameters(script_name, kwargs)

        if not is_valid:
            logging.error(f"Error en script global '{script_name}': {error_msg}")
            return

        # Obtener función real desde definición
        script_def = get_global_script(script_name)
        if not script_def:
            logging.warning(f"Script global desconocido: {script_name}")
            return

        # Buscar función en registry
        script_function_name = script_def.script_function

        if script_function_name not in SCRIPT_REGISTRY:
            logging.error(f"Función de script '{script_function_name}' no registrada.")
            return

        script_function = SCRIPT_REGISTRY[script_function_name]

    else:
        # Script normal (v1.0)
        if script_name not in SCRIPT_REGISTRY:
            logging.warning(f"Script desconocido: {script_name}")
            return

        script_function = SCRIPT_REGISTRY[script_name]

    # Ejecutar
    try:
        result = await script_function(session=session, **context, **kwargs)
        return result
    except Exception:
        logging.exception(f"Error ejecutando script '{script_name}'")
        return None


# Agregar nuevas funciones de scripts globales al registry
async def script_danar_area(
    session: AsyncSession,
    room: Room,
    cantidad: int = 10,
    tipo: str = "fuego",
    mensaje: str = None,
    **kwargs
):
    """Script global: Daña a todos los personajes en una sala."""
    from src.services import broadcaster_service, online_service
    from sqlalchemy import select
    from src.models import Character

    # Obtener personajes en la sala
    query = select(Character).where(Character.room_id == room.id)
    result = await session.execute(query)
    characters = result.scalars().all()

    for character in characters:
        # Verificar online
        is_online = await online_service.is_character_online(character.id)
        if not is_online:
            continue

        # Aplicar daño (requiere sistema de stats)
        # character.hp -= cantidad

        # Mensaje personalizado
        msg = mensaje or f"Una ola de {tipo} te golpea, causando {cantidad} de daño."
        msg = msg.replace("{tipo}", tipo).replace("{cantidad}", str(cantidad))

        await broadcaster_service.send_message_to_character(
            character,
            f"❌ {msg}"
        )


async def script_curar_area(
    session: AsyncSession,
    room: Room,
    cantidad: int = 5,
    **kwargs
):
    """Script global: Cura a todos los personajes en una sala."""
    from src.services import broadcaster_service, online_service
    from sqlalchemy import select
    from src.models import Character

    query = select(Character).where(Character.room_id == room.id)
    result = await session.execute(query)
    characters = result.scalars().all()

    for character in characters:
        is_online = await online_service.is_character_online(character.id)
        if not is_online:
            continue

        # Aplicar curación (requiere sistema de stats)
        # character.hp = min(character.max_hp, character.hp + cantidad)

        await broadcaster_service.send_message_to_character(
            character,
            f"✅ Una energía curativa te restaura {cantidad} puntos de vida."
        )


# Registrar nuevos scripts
SCRIPT_REGISTRY.update({
    "script_danar_area": script_danar_area,
    "script_curar_area": script_curar_area,
    # ... más scripts globales
})
```

#### 3.3 Uso en Prototipos

```python
# game_data/item_prototypes.py

"volcan_activo": {
    "name": "un volcán activo",
    "description": "Lava burbujea en el cráter.",
    "tick_scripts": [
        {
            "interval_ticks": 150,  # Cada 300 segundos
            # v1.0 - Script normal
            # "script": "script_danar_area(cantidad=20, tipo=lava)"

            # v2.0 - Global script (con validación)
            "script": "global.danar_area(cantidad=20, tipo=fuego, mensaje=La lava te quema!)",
            "category": "ambient",
            "permanent": True
        }
    ]
}

"fuente_curativa": {
    "name": "una fuente curativa",
    "tick_scripts": [{
        "interval_ticks": 60,
        "script": "global.curar_area(cantidad=5)",
        "category": "ambient",
        "permanent": True
    }]
}

"trampa_teleport": {
    "scripts": {
        "on_enter": "global.teleport_aleatorio(tag=mazmorra, excluir_actual=true)"
    }
}
```

#### 3.4 Ventajas

✅ **DRY**: No duplicar código, definir una vez y reutilizar
✅ **Validación**: Parámetros validados contra definición (tipos, rangos, valores permitidos)
✅ **Documentación**: Auto-documentado con descriptions y examples
✅ **Type safety**: Errores detectados antes de ejecutar
✅ **Categorización**: Scripts organizados por categoría (combat, healing, movement, etc.)

---

### Componente 4: State Manager (Gestión de Estado)

**Objetivo**: Permitir que scripts guarden datos persistentes entre ejecuciones.

#### 4.1 Diseño

**Archivo**: `src/services/state_manager.py`

```python
from typing import Any, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
import redis.asyncio as redis
import json
import logging

from src.config import settings
from src.models import Item, Room


class StateManager:
    """
    Gestor de estado para scripts.

    Soporta dos tipos de estado:
    - Persistente: Se guarda en BD (JSONB), sobrevive reinicios
    - Transient: Se guarda en Redis, no sobrevive reinicios
    """

    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None

    async def initialize(self):
        """Inicializa la conexión a Redis."""
        self._redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def close(self):
        """Cierra la conexión a Redis."""
        if self._redis_client:
            await self._redis_client.close()

    # =================== ESTADO PERSISTENTE (PostgreSQL) ===================

    async def get_persistent_state(
        self,
        session: AsyncSession,
        entity: Any,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Obtiene un valor del estado persistente de una entidad.

        Args:
            session: Sesión de BD
            entity: La entidad (Item, Room, etc.)
            key: Clave del estado
            default: Valor por defecto si no existe
        """
        if not hasattr(entity, 'script_state'):
            return default

        script_state = entity.script_state or {}
        return script_state.get(key, default)

    async def set_persistent_state(
        self,
        session: AsyncSession,
        entity: Any,
        key: str,
        value: Any
    ):
        """
        Establece un valor en el estado persistente de una entidad.

        El cambio se guarda en la BD cuando se haga commit.
        """
        if not hasattr(entity, 'script_state'):
            logging.warning(f"Entidad {type(entity)} no tiene campo script_state")
            return

        if entity.script_state is None:
            entity.script_state = {}

        entity.script_state[key] = value

        # Marcar como modificado para que SQLAlchemy detecte el cambio
        flag_modified(entity, "script_state")

    async def increment_persistent_counter(
        self,
        session: AsyncSession,
        entity: Any,
        key: str,
        amount: int = 1
    ) -> int:
        """
        Incrementa un contador persistente y retorna el nuevo valor.
        """
        current = await self.get_persistent_state(session, entity, key, default=0)
        new_value = current + amount
        await self.set_persistent_state(session, entity, key, new_value)
        return new_value

    async def get_all_persistent_state(
        self,
        session: AsyncSession,
        entity: Any
    ) -> Dict[str, Any]:
        """Obtiene todo el estado persistente de una entidad."""
        if not hasattr(entity, 'script_state'):
            return {}
        return entity.script_state or {}

    # =================== ESTADO TRANSIENT (Redis) ===================

    def _make_redis_key(self, entity_type: str, entity_id: int, key: str) -> str:
        """Genera una clave única de Redis."""
        return f"script_state:{entity_type}:{entity_id}:{key}"

    async def get_transient_state(
        self,
        entity_type: str,
        entity_id: int,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Obtiene un valor del estado transient (Redis).

        Útil para datos temporales que no necesitan persistir.
        """
        redis_key = self._make_redis_key(entity_type, entity_id, key)

        try:
            value = await self._redis_client.get(redis_key)
            if value is None:
                return default

            # Deserializar JSON
            return json.loads(value)
        except Exception:
            logging.exception(f"Error obteniendo estado transient: {redis_key}")
            return default

    async def set_transient_state(
        self,
        entity_type: str,
        entity_id: int,
        key: str,
        value: Any,
        expire_seconds: Optional[int] = None
    ):
        """
        Establece un valor en el estado transient (Redis).

        Args:
            expire_seconds: Tiempo de expiración en segundos (opcional)
        """
        redis_key = self._make_redis_key(entity_type, entity_id, key)

        try:
            # Serializar a JSON
            json_value = json.dumps(value)

            if expire_seconds:
                await self._redis_client.setex(redis_key, expire_seconds, json_value)
            else:
                await self._redis_client.set(redis_key, json_value)
        except Exception:
            logging.exception(f"Error guardando estado transient: {redis_key}")

    async def delete_transient_state(
        self,
        entity_type: str,
        entity_id: int,
        key: str
    ):
        """Elimina un valor del estado transient."""
        redis_key = self._make_redis_key(entity_type, entity_id, key)
        await self._redis_client.delete(redis_key)


# Instancia singleton
state_manager = StateManager()
```

#### 4.2 Migración de BD (Agregar columna script_state)

**Archivo**: `alembic/versions/XXXX_add_script_state.py`

```python
"""Add script_state column to Item and Room

Revision ID: XXXX
Revises: YYYY
Create Date: 2025-01-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


def upgrade():
    # Agregar script_state a Item
    op.add_column('items', sa.Column('script_state', JSONB, nullable=True))

    # Agregar script_state a Room
    op.add_column('rooms', sa.Column('script_state', JSONB, nullable=True))


def downgrade():
    op.drop_column('items', 'script_state')
    op.drop_column('rooms', 'script_state')
```

#### 4.3 Uso en Scripts

```python
# src/services/script_service.py

# Ejemplo: Script que cuenta visitantes de una sala
async def script_contar_visitantes(
    session: AsyncSession,
    room: Room,
    character: Character,
    **kwargs
):
    """
    Script que incrementa un contador de visitantes únicos.
    """
    from src.services.state_manager import state_manager

    # Obtener lista de visitantes
    visitantes = await state_manager.get_persistent_state(
        session,
        room,
        "visitantes",
        default=[]
    )

    # Agregar character si no está
    if character.id not in visitantes:
        visitantes.append(character.id)

        await state_manager.set_persistent_state(
            session,
            room,
            "visitantes",
            visitantes
        )

        # Incrementar contador total
        total = await state_manager.increment_persistent_counter(
            session,
            room,
            "visitantes_totales"
        )

        await broadcaster_service.send_message_to_character(
            character,
            f"<i>Eres el visitante número {total} de esta sala.</i>"
        )


# Ejemplo: Puerta que se puede abrir solo 3 veces
async def script_desgastar_puerta(
    session: AsyncSession,
    target: Item,
    character: Character,
    **kwargs
):
    """
    Script que reduce los usos restantes de una puerta frágil.
    """
    from src.services.state_manager import state_manager

    # Obtener usos restantes
    usos = await state_manager.get_persistent_state(
        session,
        target,
        "usos_restantes",
        default=3
    )

    if usos <= 0:
        await broadcaster_service.send_message_to_character(
            character,
            "❌ La puerta está rota y no se puede abrir."
        )
        return False  # Cancelar acción

    # Decrementar usos
    nuevo_usos = usos - 1
    await state_manager.set_persistent_state(
        session,
        target,
        "usos_restantes",
        nuevo_usos
    )

    if nuevo_usos == 0:
        await state_manager.set_persistent_state(
            session,
            target,
            "rota",
            True
        )

        await broadcaster_service.send_message_to_room(
            session,
            character.room.id,
            "<i>La puerta se rompe con un crujido ominoso.</i>",
            exclude_character_id=character.id
        )
    else:
        await broadcaster_service.send_message_to_character(
            character,
            f"⚠️ La puerta cruje. Le quedan {nuevo_usos} usos antes de romperse."
        )

    return True  # Permitir acción


# Registrar scripts
SCRIPT_REGISTRY.update({
    "script_contar_visitantes": script_contar_visitantes,
    "script_desgastar_puerta": script_desgastar_puerta,
})
```

#### 4.4 Uso en Prototipos

```python
# game_data/item_prototypes.py

"puerta_fragil": {
    "name": "una puerta frágil",
    "description": "Una puerta de madera vieja que parece estar a punto de romperse.",
    "scripts": {
        "before_open": "script_desgastar_puerta"
    },
    # Estado inicial (opcional, se puede omitir y usar defaults en script)
    "script_state": {
        "usos_restantes": 3,
        "rota": False
    }
}

# game_data/room_prototypes.py
"sala_museo": {
    "name": "Museo de Runegard",
    "description": "Un antiguo museo lleno de reliquias.",
    "scripts": {
        "on_enter": "script_contar_visitantes"
    },
    "script_state": {
        "visitantes": [],
        "visitantes_totales": 0
    }
}
```

#### 4.5 Ventajas

✅ **Persistencia**: Estado sobrevive reinicios del bot
✅ **Flexibilidad**: Dos tipos de estado (persistente vs transient)
✅ **Performance**: Estado transient en Redis (rápido, no satura BD)
✅ **Type-safe**: JSONB permite tipos complejos (listas, dicts)
✅ **Atómico**: Operaciones como increment son seguras

---

### Componente 5: Priority System (Gestión de Prioridades)

**Objetivo**: Controlar el orden de ejecución cuando múltiples scripts se disparan.

#### 5.1 Diseño

Extender el formato de scripts en prototipos para soportar múltiples scripts por evento:

```python
# game_data/item_prototypes.py

"item_complejo": {
    "scripts": {
        "on_get": [
            {
                "script": "script_verificar_permiso",
                "priority": 100,  # Mayor = ejecuta primero
                "phase": "before"
            },
            {
                "script": "script_registrar_obtención",
                "priority": 50,
                "phase": "after"
            },
            {
                "script": "script_notificar_sala",
                "priority": 10,
                "phase": "after"
            }
        ]
    }
}
```

#### 5.2 Actualización de Event Hub

```python
# src/services/event_hub.py

async def _execute_entity_scripts(
    self,
    entity: Any,
    event_name: str,
    context: EventContext,
    phase: EventPhase
) -> EventResult:
    """
    Ejecuta scripts con soporte de prioridades.
    """
    from src.services import script_service

    if not hasattr(entity, 'prototype'):
        return EventResult(success=True)

    prototype = entity.prototype
    scripts = prototype.get("scripts", {})

    # Obtener scripts para este evento
    event_scripts = scripts.get(event_name)

    if not event_scripts:
        return EventResult(success=True)

    # Normalizar a lista de scripts
    if isinstance(event_scripts, str):
        # Formato simple (v1.0)
        script_list = [{
            "script": event_scripts,
            "priority": 0,
            "phase": phase.value
        }]
    elif isinstance(event_scripts, list):
        # Formato con prioridades (v2.0)
        script_list = event_scripts
    else:
        return EventResult(success=True)

    # Filtrar por fase
    script_list = [
        s for s in script_list
        if s.get("phase", "after") == phase.value
    ]

    # Ordenar por prioridad (mayor primero)
    script_list.sort(key=lambda s: s.get("priority", 0), reverse=True)

    # Ejecutar en orden
    for script_def in script_list:
        script_string = script_def.get("script")

        if not script_string:
            continue

        try:
            result = await script_service.execute_script(
                script_string=script_string,
                session=context.session,
                character=context.character,
                target=context.target,
                room=context.room,
                **context.extra
            )

            # Si script retorna False en fase BEFORE, cancelar
            if phase == EventPhase.BEFORE and result is False:
                return EventResult(
                    success=True,
                    cancel_action=True,
                    message=script_def.get("cancel_message", "La acción fue cancelada.")
                )

        except Exception:
            logging.exception(f"Error ejecutando script: {script_string}")

    return EventResult(success=True)
```

#### 5.3 Ventajas

✅ **Control de orden**: Scripts críticos (validaciones) ejecutan primero
✅ **Cancelación**: Scripts before pueden prevenir la acción
✅ **Retrocompatible**: String simple sigue funcionando
✅ **Explícito**: Prioridad visible en prototipo

---

## 📅 Plan de Implementación

### Fase 1: Event Hub (1 semana)

**Objetivo**: Sistema centralizado de eventos.

**Tareas**:
1. Crear `src/services/event_hub.py` con EventHub class
2. Definir EventType enum con todos los eventos
3. Implementar trigger_event() y execute_entity_scripts()
4. Migrar CmdLook para usar Event Hub
5. Migrar CmdGet, CmdDrop, CmdPut, CmdTake
6. Testing exhaustivo con scripts existentes
7. Documentar en `docs/sistemas-del-motor/event-hub.md`

**Criterio de Éxito**:
- ✅ Todos los comandos de items usan Event Hub
- ✅ Scripts v1.0 siguen funcionando sin cambios
- ✅ Se pueden agregar nuevos eventos fácilmente

### Fase 2: Cron Scheduler (1 semana)

**Objetivo**: Scheduling calendario-based.

**Tareas**:
1. Crear `src/services/enhanced_scheduler.py`
2. Implementar CronTrigger parsing con croniter
3. Sistema de cache de cron scripts
4. Job para recargar scripts cada 5 minutos
5. Soportar scripts globales (global: true)
6. Testing con múltiples expresiones cron
7. Documentar en `docs/sistemas-del-motor/enhanced-scheduler.md`

**Criterio de Éxito**:
- ✅ Scripts cron se ejecutan en horarios correctos
- ✅ Scripts globales no duplican ejecución
- ✅ Performance < 100ms por verificación de cron

### Fase 3: Global Scripts (1 semana)

**Objetivo**: Scripts reutilizables con validación.

**Tareas**:
1. Crear `game_data/global_scripts.py`
2. Definir GlobalScriptDefinition con parameters
3. Implementar validate_script_parameters()
4. Actualizar parser de script_service para soportar "global."
5. Crear 10 global scripts de ejemplo
6. Comando admin `/listarglobalscripts` para ver catálogo
7. Documentar en `docs/creacion-de-contenido/global-scripts.md`

**Criterio de Éxito**:
- ✅ Scripts globales validados antes de ejecutar
- ✅ Errores claros si parámetros inválidos
- ✅ Documentación auto-generada para diseñadores

### Fase 4: Enhanced Parser (3 días)

**Objetivo**: Parser que soporta tipos complejos.

**Tareas**:
1. Implementar _parse_advanced_arguments() con shlex
2. Soportar strings con espacios (comillas)
3. Soportar listas simples: [item1, item2]
4. Soportar booleanos: true/false
5. Testing exhaustivo de edge cases
6. Documentar sintaxis en `docs/creacion-de-contenido/sintaxis-de-scripts.md`

**Criterio de Éxito**:
- ✅ Strings complejos funcionan correctamente
- ✅ Listas y booleanos se parsean bien
- ✅ Parser no rompe scripts v1.0

### Fase 5: State Manager (4 días)

**Objetivo**: Gestión de estado persistente y transient.

**Tareas**:
1. Crear `src/services/state_manager.py`
2. Migración BD: agregar columna `script_state` JSONB
3. Implementar get/set para estado persistente
4. Implementar get/set para estado transient (Redis)
5. Helpers: increment_counter(), get_all_state()
6. Testing de persistencia (reiniciar bot, verificar datos)
7. Documentar en `docs/sistemas-del-motor/state-manager.md`

**Criterio de Éxito**:
- ✅ Estado persiste entre reinicios
- ✅ Estado transient funciona con Redis
- ✅ Scripts pueden guardar/leer datos correctamente

### Fase 6: Priority System (2 días)

**Objetivo**: Control de orden de ejecución.

**Tareas**:
1. Actualizar Event Hub para soportar lista de scripts
2. Implementar sorting por prioridad
3. Soportar cancelación en before phase
4. Testing con scripts que retornan False
5. Documentar en `docs/sistemas-del-motor/priority-system.md`

**Criterio de Éxito**:
- ✅ Scripts se ejecutan en orden de prioridad
- ✅ Scripts before pueden cancelar acciones
- ✅ Formato simple (string) sigue funcionando

### Fase 7: Performance Optimization (3 días)

**Objetivo**: Optimizar para escala.

**Tareas**:
1. Agregar índice en columna script_state
2. Optimizar query de tick scripts (solo cargar items con scripts)
3. Batch loading de personajes en salas
4. Cache de prototipos más usados
5. Profiling con 1000+ items con scripts
6. Documentar optimizaciones en `docs/arquitectura/performance-scripts.md`

**Criterio de Éxito**:
- ✅ Pulse tick < 500ms con 10,000 items
- ✅ Cron verification < 100ms
- ✅ Memoria estable durante 24h

### Fase 8: Documentación Completa (2 días)

**Objetivo**: Documentación exhaustiva para desarrolladores y diseñadores.

**Tareas**:
1. Guía completa de Event Hub
2. Tutorial de Cron Scheduler con ejemplos
3. Catálogo de Global Scripts
4. Guía de State Management
5. Cookbook con 20+ ejemplos de scripts
6. Actualizar CLAUDE.md con sistema v2.0
7. Video tutorial (opcional)

**Criterio de Éxito**:
- ✅ Diseñadores pueden crear scripts sin ayuda de devs
- ✅ Todos los features documentados con ejemplos
- ✅ CLAUDE.md refleja sistema v2.0

---

## ⚡ Consideraciones de Performance

### 1. Query Optimization

**Problema**: Cargar TODOS los items en cada tick es ineficiente.

**Solución**: Agregar filtro en query para solo cargar items con scripts.

```python
# Opción A: Usar filtro JSON (PostgreSQL 9.4+)
query = select(Item).where(
    Item.prototype['tick_scripts'].astext != None
)

# Opción B: Agregar columna booleana has_scripts
# Migración:
op.add_column('items', sa.Column('has_tick_scripts', sa.Boolean, default=False))

# Query:
query = select(Item).where(Item.has_tick_scripts == True)
```

### 2. Batch Processing

**Problema**: Ejecutar queries individuales por cada personaje en sala.

**Solución**: Batch loading con selectinload.

```python
# Malo
for char_id in char_ids:
    character = await session.get(Character, char_id)

# Bueno
query = select(Character).where(Character.id.in_(char_ids)).options(
    selectinload(Character.room),
    selectinload(Character.inventory)
)
characters = (await session.execute(query)).scalars().all()
```

### 3. Cache de Prototipos

**Problema**: Parsear prototipos (TOML/dict) en cada ejecución.

**Solución**: Cache en memoria de prototipos usados frecuentemente.

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_prototype(entity_type: str, key: str) -> dict:
    """Cache de prototipos más usados."""
    if entity_type == "item":
        from game_data.item_prototypes import ITEM_PROTOTYPES
        return ITEM_PROTOTYPES.get(key, {})
    # ...
```

### 4. Redis para Estado Transient

**Problema**: Saturar BD con datos temporales.

**Solución**: Usar Redis para datos que no necesitan persistir.

```python
# Ejemplo: Cooldowns de habilidades
await state_manager.set_transient_state(
    "character",
    character.id,
    "cooldown_fireball",
    True,
    expire_seconds=10  # Auto-expira en 10s
)
```

### 5. Profiling y Monitoring

**Herramientas**:
- `cProfile` para profiling de Python
- `pg_stat_statements` para queries lentas en PostgreSQL
- Prometheus + Grafana para métricas en producción

**Métricas clave**:
- Tiempo de ejecución de pulse tick
- Número de scripts ejecutados por tick
- Queries SQL ejecutadas por tick
- Memoria usada por cache

---

## 🔄 Migración y Retrocompatibilidad

### Estrategia de Migración: Zero Breaking Changes

**Principio**: Scripts v1.0 DEBEN seguir funcionando sin modificar.

### Compatibilidad de Formatos

#### Formato v1.0 (sigue funcionando)
```python
"espada": {
    "scripts": {
        "on_look": "script_notificar_brillo_magico(color=rojo)"
    },
    "tick_scripts": [{
        "interval_ticks": 60,
        "script": "script_susurro",
        "permanent": True
    }]
}
```

#### Formato v2.0 (nuevas features)
```python
"espada": {
    "scripts": {
        # Simple (v1.0)
        "on_look": "script_notificar_brillo_magico(color=rojo)",

        # Before/After (v2.0)
        "before_get": "script_verificar_permiso",
        "after_get": "script_vincular_alma",

        # Con prioridades (v2.0)
        "on_use": [
            {"script": "script_validar", "priority": 100, "phase": "before"},
            {"script": "script_ejecutar", "priority": 50, "phase": "after"}
        ]
    },
    "tick_scripts": [{
        # Tick-based (v1.0)
        "interval_ticks": 60,
        "script": "script_susurro",
        "permanent": True
    }],
    "scheduled_scripts": [{
        # Cron-based (v2.0)
        "schedule": "0 10 * * MON",
        "script": "script_evento",
        "permanent": True,
        "global": True
    }],
    "script_state": {
        # Estado persistente (v2.0)
        "contador": 0,
        "ultimo_uso": null
    }
}
```

### Detección Automática de Formato

```python
def normalize_script_definition(scripts_dict: dict, event_name: str) -> list:
    """
    Normaliza scripts de v1.0 y v2.0 a formato unificado.

    v1.0: "on_look": "script()"
    v2.0: "on_look": [{"script": "script()", "priority": 0}]

    Returns:
        Lista normalizada de scripts con prioridad.
    """
    event_scripts = scripts_dict.get(event_name)

    if not event_scripts:
        return []

    # v1.0: String simple
    if isinstance(event_scripts, str):
        return [{
            "script": event_scripts,
            "priority": 0,
            "phase": "after"
        }]

    # v2.0: Lista de scripts
    if isinstance(event_scripts, list):
        # Normalizar cada script
        normalized = []
        for script_def in event_scripts:
            if isinstance(script_def, str):
                # Soporte de lista de strings: ["script1", "script2"]
                normalized.append({
                    "script": script_def,
                    "priority": 0,
                    "phase": "after"
                })
            elif isinstance(script_def, dict):
                # Ya está en formato v2.0
                normalized.append({
                    "script": script_def.get("script"),
                    "priority": script_def.get("priority", 0),
                    "phase": script_def.get("phase", "after")
                })
        return normalized

    return []
```

### Plan de Actualización de Prototipos Existentes

**No es necesario actualizar inmediatamente**. Los prototipos v1.0 siguen funcionando.

**Actualización progresiva**:
1. Identificar prototipos que se beneficiarían de nuevas features
2. Actualizar uno por uno según necesidad
3. Usar comandos admin para testing: `/testscript item_key on_get`

### Testing de Retrocompatibilidad

**Test suite obligatorio antes de release**:

```python
# tests/test_script_compatibility.py

async def test_v1_simple_script_still_works():
    """Scripts v1.0 con string simple deben funcionar."""
    prototype = {
        "scripts": {
            "on_look": "script_notificar_brillo_magico(color=rojo)"
        }
    }
    # ... test execution

async def test_v1_tick_scripts_still_work():
    """Tick scripts v1.0 deben funcionar sin cambios."""
    prototype = {
        "tick_scripts": [{
            "interval_ticks": 60,
            "script": "script_susurro",
            "permanent": True
        }]
    }
    # ... test execution

async def test_mixed_v1_v2_scripts():
    """Mezclar scripts v1.0 y v2.0 en mismo prototipo."""
    prototype = {
        "scripts": {
            "on_look": "script_brillo",  # v1.0
            "on_get": [  # v2.0
                {"script": "script_validar", "priority": 100}
            ]
        }
    }
    # ... test execution
```

---

## 📚 Referencias y Recursos

### Librerías Externas

1. **croniter** (Cron parsing)
   - Docs: https://github.com/kiorky/croniter
   - Instalación: `pip install croniter`
   - Uso: Parsear expresiones cron y calcular próximas ejecuciones

2. **shlex** (Parser avanzado)
   - Docs: https://docs.python.org/3/library/shlex.html
   - Built-in de Python
   - Uso: Parsear argumentos complejos con comillas

3. **APScheduler** (Ya en uso)
   - Docs: https://apscheduler.readthedocs.io/
   - Usado para pulse actual y cron scheduler

### Patrones de Diseño

1. **Event-Driven Architecture**
   - Observer Pattern para hooks globales
   - Command Pattern para scripts

2. **Registry Pattern**
   - SCRIPT_REGISTRY
   - GLOBAL_SCRIPTS

3. **State Pattern**
   - StateManager con persistente/transient

4. **Strategy Pattern**
   - Diferentes tipos de scheduling (tick, cron, timestamp)

### Documentos Relacionados del Proyecto

- `docs/sistemas-del-motor/sistema-de-scripts.md` (actual v1.0)
- `docs/sistemas-del-motor/sistema-de-pulso.md`
- `docs/creacion-de-contenido/escritura-de-scripts.md`
- `CLAUDE.md` (filosofía motor/contenido)

### Recursos de Aprendizaje

1. **MUD Development**
   - Evennia: https://www.evennia.com/docs/latest/
   - Lección: Sistema de eventos y hooks

2. **Game Scripting**
   - Unreal Blueprint
   - Lección: Visual scripting con validación

3. **Cron Expressions**
   - Crontab Guru: https://crontab.guru/
   - Lección: Testing de expresiones cron

---

## 🎯 Resumen Ejecutivo para Implementación

### Prioridad Alta (Must Have - Implementar Primero)

1. **Event Hub** (Fase 1)
   - Desbloquea extensibilidad de eventos
   - 1 semana de desarrollo
   - ROI inmediato

2. **State Manager** (Fase 5)
   - Necesario para casos de uso avanzados
   - 4 días de desarrollo
   - Habilita scripts con memoria

3. **Cron Scheduler** (Fase 2)
   - Feature solicitada específicamente por usuario
   - 1 semana de desarrollo
   - Valor inmediato para diseñadores

### Prioridad Media (Should Have - Implementar Después)

4. **Global Scripts** (Fase 3)
   - Mejora DX significativa
   - 1 semana de desarrollo
   - Reduce duplicación de código

5. **Priority System** (Fase 6)
   - Control fino de ejecución
   - 2 días de desarrollo
   - Nice-to-have para scripts complejos

### Prioridad Baja (Nice to Have - Implementar Si Hay Tiempo)

6. **Enhanced Parser** (Fase 4)
   - QoL improvement
   - 3 días de desarrollo
   - No bloqueante

7. **Performance Optimization** (Fase 7)
   - Solo necesario cuando haya muchos scripts activos
   - 3 días de desarrollo
   - Implementar cuando escala lo requiera

### Timeline Estimado

**MVP (Mínimo Viable Product)**:
- Fase 1 + Fase 2 + Fase 5 = **2.5 semanas**
- Features: Event hooks, Cron scheduling, Estado persistente

**Implementación Completa**:
- Todas las fases = **3-4 semanas**
- Features: Todo lo propuesto + optimizaciones + docs

### Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Romper scripts v1.0 | Baja | Alto | Testing exhaustivo de retrocompatibilidad |
| Performance con muchos scripts | Media | Medio | Fase 7 de optimización, profiling continuo |
| Complejidad de cron parsing | Baja | Bajo | Usar librería probada (croniter) |
| Estado inconsistente | Media | Alto | Validación en State Manager, tests |

---

## 🚀 Próximos Pasos Recomendados

1. **Revisar esta propuesta** con el equipo de desarrollo
2. **Priorizar fases** según necesidades inmediatas del juego
3. **Crear tickets/issues** en GitHub para cada fase
4. **Implementar Fase 1 (Event Hub)** como POC
5. **Recopilar feedback** de diseñadores de contenido
6. **Iterar** basándose en uso real

---

**Fin del Documento**

> **Versión**: 2.0
> **Fecha**: 2025-01-16
> **Autor**: Claude (Análisis solicitado por Usuario)
> **Estado**: Propuesta completa lista para implementación
> **Caracteres UTF-8**: Verificados y corregidos
