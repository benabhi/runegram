---
título: "Sistema de Validación"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["validación", "integridad", "fail-fast", "prototipos"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-prototipos.md"
  - "sistemas-del-motor/sistema-de-comandos.md"
referencias_código:
  - "src/services/validation_service.py"
  - "run.py"
estado: "actual"
---

# Validation System

El Sistema de Validación es una capa de seguridad crítica que detecta errores de configuración y conflictos en los datos del juego **antes** de que causen problemas durante la ejecución. Sigue el principio de diseño **"Fail Fast"**: es mejor que el bot no arranque con un error claro, que arranque con configuraciones conflictivas que causen bugs difíciles de diagnosticar.

## Filosofía

### Principio "Fail Fast"

En lugar de permitir que el bot arranque con configuraciones problemáticas que podrían causar comportamientos impredecibles o bugs sutiles durante el juego, el sistema de validación:

1. **Detecta** problemas comunes al arranque
2. **Reporta** errores claros y accionables
3. **Previene** el arranque si hay problemas críticos

Este enfoque reduce drásticamente el tiempo de debugging y hace que los errores sean obvios e inmediatos.

### Single Source of Truth

Cada identificador en el sistema debe ser único en su dominio:
- Los **aliases de comandos** no deben duplicarse entre CommandSets
- Las **keys de prototipos** (rooms, items, channels) deben ser únicas dentro de su tipo
- Las **referencias** (como salidas de salas) deben apuntar a entidades existentes

## Implementación

### Ubicación

**Archivo principal:** `src/services/validation_service.py`

El servicio de validación está centralizado en un único módulo que proporciona:
- Funciones de validación específicas para cada dominio
- Una función `validate_all()` que ejecuta todas las validaciones
- Una función `get_validation_report()` para diagnóstico

### Integración en el Arranque

**Ubicación:** `run.py:on_startup()`

La validación se ejecuta como **primer paso** en la secuencia de arranque del bot, antes de:
- Inicializar el scheduler
- Sincronizar el mundo desde prototipos
- Cargar tickers
- Cualquier otra inicialización

```python
async def on_startup(dispatcher):
    try:
        # 0. VALIDACIONES CRÍTICAS: Ejecutar antes de cualquier inicialización.
        validation_service.validate_all()  # ← Aquí

        # 1. Resto de la secuencia de arranque...
        ticker_service.initialize_scheduler()
        # ...
```

Si `validate_all()` lanza una `ValidationError`, el bot no arrancará y se mostrará un mensaje de error detallado en los logs.

## Validaciones Implementadas

### 1. Validación de Aliases de Comandos

**Función:** `validate_command_aliases()`

**Propósito:** Detectar aliases duplicados entre todos los comandos del juego.

**Problema que resuelve:**
```
Usuario escribe: /n
Sistema confundido: ¿Es /norte o /novato?
```

**Qué valida:**
- Recopila **todos** los aliases de **todos** los CommandSets (incluyendo dinámicos)
- Identifica cualquier alias que aparezca en más de un comando
- Reporta exactamente dónde está el conflicto

**Ejemplo de error:**
```
❌ Alias de comando duplicado: '/n' está definido en: movement.norte, channels.novato
```

### 2. Validación de Keys de Prototipos de Salas

**Función:** `validate_room_prototype_keys()`

**Propósito:** Asegurar la integridad de las definiciones de salas.

**Qué valida:**
- **Unicidad:** No puede haber dos salas con la misma key
- **Referencias válidas:** Todas las salidas deben apuntar a salas que existen

**Ejemplo de errores:**
```
❌ Key de sala duplicada: 'plaza_central' aparece más de una vez en ROOM_PROTOTYPES

❌ Salida inválida en sala 'posada': la dirección 'arriba' apunta a 'habitacion_secreta' que no existe
```

**Soporte para formatos de salida:**

El validador soporta tanto el formato simple como el formato con locks:
```python
# Formato simple (string)
"exits": {
    "norte": "plaza_central"
}

# Formato con locks (dict)
"exits": {
    "norte": {
        "to": "torre_mago",
        "locks": "nivel(5)"
    }
}
```

### 3. Validación de Keys de Prototipos de Items

**Función:** `validate_item_prototype_keys()`

**Propósito:** Asegurar que no haya keys de items duplicadas.

**Qué valida:**
- Unicidad de keys en `ITEM_PROTOTYPES`

**Ejemplo de error:**
```
❌ Key de item duplicada: 'espada_hierro' aparece más de una vez en ITEM_PROTOTYPES
```

### 4. Validación de Keys de Prototipos de Canales

**Función:** `validate_channel_prototype_keys()`

**Propósito:** Asegurar que no haya keys de canales duplicadas.

**Qué valida:**
- Unicidad de keys en `CHANNEL_PROTOTYPES`

**Ejemplo de error:**
```
❌ Key de canal duplicada: 'novato' aparece más de una vez en CHANNEL_PROTOTYPES
```

## Uso del Sistema

### Durante el Arranque (Automático)

El sistema se ejecuta automáticamente cada vez que el bot arranca. No requiere ninguna acción manual.

**Si hay errores:**
```
2025-01-15 10:30:45 [ERROR] - src.services.validation_service:

⚠️  ERRORES DE VALIDACIÓN DETECTADOS ⚠️
============================================================
❌ Alias de comando duplicado: '/n' está definido en: movement.norte, channels.novato
❌ Salida inválida en sala 'templo': la dirección 'dentro' apunta a 'sanctum' que no existe
============================================================

Corrige estos errores antes de continuar.
```

El bot se detendrá y no arrancará hasta que se corrijan los errores.

**Si todo está bien:**
```
2025-01-15 10:30:45 [INFO] - src.services.validation_service: 🔍 Ejecutando validaciones de integridad del motor...
2025-01-15 10:30:45 [INFO] - src.services.validation_service: ✅ Todas las validaciones pasaron correctamente.
```

### Comando de Diagnóstico (Manual)

**Comando:** `/validar` o `/reportevalidacion`

**Permisos:** `rol(ADMIN)`

**Propósito:** Ejecutar las validaciones en tiempo real sin reiniciar el bot.

**Uso:**
```
> /validar

=== REPORTE DE VALIDACIÓN ===

✅ No se encontraron errores.

📊 ESTADÍSTICAS:
  • Aliases de comandos: 47
  • Prototipos de salas: 8
  • Prototipos de items: 23
  • Prototipos de canales: 2
```

**Con errores:**
```
> /validar

=== REPORTE DE VALIDACIÓN ===

❌ ERRORES ENCONTRADOS:
  ❌ Alias de comando duplicado: '/n' está definido en: movement.norte, channels.novato

📊 ESTADÍSTICAS:
  • Aliases de comandos: 47
  • Prototipos de salas: 8
  • Prototipos de items: 23
  • Prototipos de canales: 2
```

## Añadiendo Nuevas Validaciones

El sistema está diseñado para ser extensible. Para añadir una nueva validación:

### 1. Crear la función de validación

Añade una nueva función en `validation_service.py`:

```python
def validate_nueva_cosa() -> List[str]:
    """
    Valida [descripción de qué valida].

    Returns:
        Lista de mensajes de error. Vacía si no hay problemas.
    """
    errors = []

    # Tu lógica de validación aquí
    if hay_problema:
        errors.append(f"❌ Descripción del problema detectado")

    return errors
```

### 2. Integrar en validate_all()

Añade la llamada en la función `validate_all()`:

```python
def validate_all() -> None:
    logging.info("🔍 Ejecutando validaciones de integridad del motor...")

    all_errors = []
    all_errors.extend(validate_command_aliases())
    all_errors.extend(validate_room_prototype_keys())
    # ... validaciones existentes ...
    all_errors.extend(validate_nueva_cosa())  # ← Nueva validación

    if all_errors:
        # ...lanzar excepción...
```

### 3. Integrar en get_validation_report()

Añade la llamada en `get_validation_report()` para que aparezca en el comando `/validar`.

## Mejores Prácticas

### 1. Ejecutar validación después de cambios en prototipos

Después de añadir o modificar prototipos:
```bash
docker-compose restart
# Revisar logs para verificar que las validaciones pasan
```

O usar el comando administrativo:
```
/validar
```

### 2. Nombres descriptivos para aliases

**❌ Malo:**
```python
names=["norte", "n"]  # "n" puede conflictuar con "novato", "notas", etc.
```

**✅ Bueno:**
```python
names=["norte", "no"]  # "no" es menos probable que cause conflictos
```

### 3. Planificar namespace de aliases

Considera reservar ciertos prefijos para tipos específicos de comandos:
- Movimiento: n, s, e, o, ar, ab, ne, no, se, so
- Canales: nv (novato), sis (sistema), com (comercio)
- Interacción: cg (coger), dj (dejar), mr (mirar)

### 4. Revisar el reporte periódicamente

Ejecuta `/validar` periódicamente durante el desarrollo para detectar problemas temprano.

## Ver También

- [Prototype System](sistema-de-prototipos.md) - Sistema de prototipos validado
- [Command System](sistema-de-comandos.md) - Comandos validados por el sistema
