# Sistema de Filtrado de Audiencia para Canales

## 📋 Problema Identificado

**Situación actual**: El sistema de canales tiene un problema de privacidad/filtrado:

- ✅ **Locks funcionan correctamente** para controlar quién puede ESCRIBIR en un canal
  - Ejemplo: Canal "moderacion" con `lock: "rol(ADMIN)"` → solo admins pueden usar `/moderacion mensaje`
- ❌ **NO hay filtrado de DESTINATARIOS** → los mensajes llegan a TODOS los suscritos
  - Problema: Si un jugador normal se suscribe a "moderacion", recibirá mensajes que solo deberían ver los admins
  - Uso actual en código: `broadcast_to_channel()` filtra solo por suscripción (`active_channels`)

**Escenario problemático real**:
```python
# En channel_prototypes.py
"moderacion": {
    "lock": "rol(ADMIN)",  # Solo admins pueden escribir
    "default_on": False
}

# Pero si un jugador hace:
/activarcanal moderacion  # ❌ Se suscribe exitosamente

# Y un admin escribe:
/moderacion Revisando apelación de Gandalf

# El jugador normal recibe el mensaje → FUGA DE PRIVACIDAD
```

---

## 🔍 Análisis de Opciones de Implementación

### Opción 1: Reutilizar Sistema de Locks con Propiedad "audience"

**Propuesta**: Agregar campo `audience` a prototipos de canales que use la misma sintaxis y motor de evaluación que `lock`.

```python
"moderacion": {
    "lock": "rol(ADMIN)",      # Quién puede escribir
    "audience": "rol(ADMIN)"    # Quién puede recibir/ver mensajes
}
```

**Ventajas**:
- ✅ Reutiliza `permission_service.py` existente (motor AST probado)
- ✅ Sintaxis consistente con locks (fácil de entender)
- ✅ Flexible (cualquier expresión de lock: `rol(ADMIN) or tiene_objeto(pase_vip)`)
- ✅ No requiere nuevo parser ni lógica de evaluación
- ✅ Backward compatible (si no hay `audience`, comportamiento actual)

**Desventajas**:
- ⚠️ Necesita evaluar permisos en cada broadcast (overhead mínimo)

---

### Opción 2: Sistema de Visibilidad Explícito

**Propuesta**: Enum de niveles de visibilidad predefinidos.

```python
"moderacion": {
    "lock": "rol(ADMIN)",
    "visibility": "ADMIN_ONLY"  # EVERYONE, ADMIN_ONLY, SUPERADMIN_ONLY
}
```

**Ventajas**:
- ✅ Simple de implementar
- ✅ Rápido de evaluar (sin parser)

**Desventajas**:
- ❌ Inflexible (solo niveles predefinidos)
- ❌ No puede expresar lógica compleja (`rol(ADMIN) or tiene_objeto(pase)`)
- ❌ Requiere agregar nuevos niveles manualmente

---

### Opción 3: Auto-suscripción Basada en Roles

**Propuesta**: El sistema suscribe automáticamente solo a ciertos roles.

```python
"moderacion": {
    "lock": "rol(ADMIN)",
    "auto_subscribe_roles": ["ADMIN", "SUPERADMIN"],
    "restrict_subscribe": True  # Bloquea suscripción manual
}
```

**Ventajas**:
- ✅ Previene suscripciones incorrectas

**Desventajas**:
- ❌ Menos flexible que locks
- ❌ Lógica de suscripción se vuelve compleja
- ❌ No puede expresar condiciones complejas

---

### Opción 4: Validación en Suscripción (No en Broadcast)

**Propuesta**: Validar permisos al suscribirse, no al recibir.

```python
# En set_channel_status()
if not await permission_service.can_execute(character, proto.get("audience")):
    raise ValueError("No tienes permiso para suscribirte a este canal")
```

**Ventajas**:
- ✅ Valida una sola vez (al suscribirse)
- ✅ No overhead en cada broadcast

**Desventajas**:
- ❌ Si un admin es degradado a jugador, seguirá suscrito
- ❌ Requiere migraciones/limpieza de suscripciones incorrectas
- ❌ Menos robusto que validar en tiempo de envío

---

## ✅ Solución Recomendada: Opción 1 + Opción 4 (Híbrido)

**Implementación de doble capa**:

1. **Validar en suscripción** (prevenir suscripciones incorrectas)
2. **Validar en broadcast** (garantizar privacidad en tiempo real)

**Ventajas del enfoque híbrido**:
- ✅ Previene suscripciones incorrectas (mejor UX, menos confusión)
- ✅ Garantiza privacidad incluso si hay datos inconsistentes
- ✅ Maneja cambios de rol dinámicamente (admin degradado → deja de recibir)
- ✅ Reutiliza sistema de locks existente (consistencia arquitectónica)

---

## 🏗️ Diseño Técnico Detallado

### 1. Actualizar Prototipos de Canales

**Archivo**: `game_data/channel_prototypes.py`

```python
CHANNEL_PROTOTYPES = {
    "moderacion": {
        "name": "Moderación",
        "icon": "🛡️",
        "description": "Canal privado para administradores (apelaciones, moderación).",
        "type": "CHAT",
        "default_on": False,
        "lock": "rol(ADMIN)",       # Quién puede escribir
        "audience": "rol(ADMIN)"     # NUEVO: Quién puede recibir/ver
    },

    "sistema": {
        "name": "Sistema",
        "icon": "⚙️",
        "description": "Anuncios del juego y notificaciones automáticas.",
        "type": "CHAT",
        "default_on": True,
        "lock": "rol(ADMIN)",
        "audience": ""  # NUEVO: Vacío = todos pueden recibir
    },

    "novato": {
        "name": "Novato",
        "icon": "📢",
        "description": "Un canal para que los nuevos aventureros pidan ayuda.",
        "type": "CHAT",
        "default_on": True,
        "lock": "",
        "audience": ""  # NUEVO: Sin restricción
    },

    # Ejemplo avanzado con lógica compleja
    "vip": {
        "name": "VIP",
        "icon": "👑",
        "description": "Canal exclusivo para miembros VIP.",
        "type": "CHAT",
        "default_on": False,
        "lock": "tiene_objeto(pase_vip) or rol(ADMIN)",
        "audience": "tiene_objeto(pase_vip) or rol(ADMIN)"
    }
}
```

**Semántica**:
- `audience = ""` → Sin restricción (todos los suscritos reciben)
- `audience = "rol(ADMIN)"` → Solo admins reciben mensajes
- `audience` puede usar CUALQUIER expresión de lock válida

---

### 2. Modificar `channel_service.broadcast_to_channel()`

**Archivo**: `src/services/channel_service.py`

**Cambios**:

```python
async def broadcast_to_channel(
    session: AsyncSession,
    channel_key: str,
    message: str,
    exclude_character_id: int | None = None
):
    """
    Envía un mensaje a todos los jugadores suscritos a un canal
    que cumplan con los requisitos de audiencia.
    """
    try:
        if channel_key not in CHANNEL_PROTOTYPES:
            logging.warning(f"Intento de transmitir a un canal desconocido: {channel_key}")
            return

        proto = CHANNEL_PROTOTYPES[channel_key]
        formatted_message = f"{proto['icon']} <b>{proto['name']}:</b> {message}"

        # NUEVO: Obtener filtro de audiencia
        audience_filter = proto.get("audience", "")

        # Obtener todos los personajes
        query = select(Character).options(
            selectinload(Character.settings),
            selectinload(Character.account)
        )
        result = await session.execute(query)
        all_characters = result.scalars().all()

        # Enviar mensaje a suscritos que cumplan con audiencia
        for char in all_characters:
            if char.id == exclude_character_id:
                continue

            # Verificar suscripción
            settings = await get_or_create_settings(session, char)
            if not await is_channel_active(settings, channel_key):
                continue

            # NUEVO: Verificar permiso de audiencia
            if audience_filter:
                can_receive, _ = await permission_service.can_execute(char, audience_filter)
                if not can_receive:
                    logging.debug(
                        f"Saltando mensaje de canal '{channel_key}' a {char.name}: "
                        "no cumple filtro de audiencia"
                    )
                    continue

            await broadcaster_service.send_message_to_character(char, formatted_message)

    except Exception:
        logging.exception(f"Error al transmitir al canal '{channel_key}'")
```

---

### 3. Validar en Suscripción

**Archivo**: `src/services/channel_service.py`

**Cambios en `set_channel_status()`**:

```python
async def set_channel_status(
    session: AsyncSession,
    character: Character,
    channel_key: str,
    activate: bool
):
    """Activa o desactiva un canal para un personaje."""
    if channel_key not in CHANNEL_PROTOTYPES:
        raise ValueError("El canal especificado no existe.")

    proto = CHANNEL_PROTOTYPES[channel_key]
    settings = await get_or_create_settings(session, character)

    # NUEVO: Validar permiso de audiencia al activar
    if activate:
        audience_filter = proto.get("audience", "")
        if audience_filter:
            can_subscribe, error_msg = await permission_service.can_execute(
                character,
                audience_filter
            )
            if not can_subscribe:
                raise ValueError(
                    f"No tienes permiso para suscribirte al canal '{proto['name']}'. "
                    "Este canal está restringido a ciertos jugadores."
                )

    active_channels_list = settings.active_channels.get("active_channels", [])

    if activate:
        if channel_key not in active_channels_list:
            active_channels_list.append(channel_key)
    else:
        if channel_key in active_channels_list:
            active_channels_list.remove(channel_key)

    settings.active_channels["active_channels"] = active_channels_list

    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(settings, "active_channels")

    await session.commit()
```

---

### 4. Actualizar Comando `/canales`

**Archivo**: `commands/player/channels.py` (comando `/canales`)

**Mejora**: Indicar visualmente canales con restricción de audiencia.

```python
# En CmdListChannels.execute()
output += "<pre>\n"
output += "CANALES DISPONIBLES:\n\n"

for channel_key, proto in CHANNEL_PROTOTYPES.items():
    # ... código existente ...

    # NUEVO: Indicador de canal restringido
    audience_filter = proto.get("audience", "")
    if audience_filter:
        # Verificar si el jugador cumple con el filtro
        can_access, _ = await permission_service.can_execute(character, audience_filter)
        if can_access:
            restriction_icon = "🔓"  # Tiene acceso
        else:
            restriction_icon = "🔒"  # Restringido
        output += f" {restriction_icon}"

    output += "\n"
output += "</pre>"
```

---

## 📝 Plan de Implementación

### Fase 1: Implementación Core (1-2 horas)

1. **Actualizar prototipos de canales**:
   - Agregar campo `audience` a todos los canales en `channel_prototypes.py`
   - Canales existentes: `audience = ""` (sin restricción)
   - Canal "moderacion": `audience = "rol(ADMIN)"`

2. **Modificar `broadcast_to_channel()`**:
   - Agregar validación de `audience` antes de enviar
   - Logging de mensajes filtrados

3. **Modificar `set_channel_status()`**:
   - Validar permiso al activar canal
   - Mensaje de error claro si no tiene permiso

4. **Tests básicos**:
   - Jugador normal intenta suscribirse a "moderacion" → Error
   - Admin se suscribe a "moderacion" → Éxito
   - Admin escribe en "moderacion" → Solo admins reciben

### Fase 2: UX Mejorada (30 min - 1 hora)

5. **Actualizar comando `/canales`**:
   - Mostrar indicador 🔒 para canales restringidos sin acceso
   - Mostrar indicador 🔓 para canales restringidos con acceso

6. **Mensajes de error personalizados**:
   - Al intentar suscribirse sin permiso: mensaje claro
   - En `/canales`: indicar qué se necesita para acceder

### Fase 3: Documentación (30 min)

7. **Actualizar documentación**:
   - `docs/sistemas-del-motor/sistema-de-canales.md`: Nueva sección "Filtrado de Audiencia"
   - `game_data/channel_prototypes.py`: Comentarios explicativos
   - Ejemplos de uso en documentación

8. **Actualizar `CLAUDE.md`**:
   - Agregar sistema de audience a lista de sistemas
   - Guía rápida para desarrolladores

---

## 🧪 Tests a Realizar

### Test 1: Restricción Básica
```
Admin: /activarcanal moderacion  → ✅ Éxito
Jugador: /activarcanal moderacion → ❌ "No tienes permiso..."
```

### Test 2: Broadcast Filtrado
```
Admin suscrito a "moderacion"
Jugador NO suscrito (por restricción)

Admin: /moderacion Mensaje secreto
→ Admin recibe mensaje
→ Jugador NO recibe nada
```

### Test 3: Cambio de Rol Dinámico
```
1. Admin se suscribe a "moderacion"
2. Admin degradado a JUGADOR (cambio de rol)
3. Otro admin: /moderacion Nuevo mensaje
→ Ex-admin NO recibe mensaje (validación en tiempo real)
```

### Test 4: Lógica Compleja
```
Canal "vip": audience = "tiene_objeto(pase_vip) or rol(ADMIN)"

Jugador con pase_vip: /activarcanal vip → ✅
Jugador sin pase: /activarcanal vip → ❌
Admin sin pase: /activarcanal vip → ✅ (por rol)
```

### Test 5: Backward Compatibility
```
Canales sin campo "audience":
→ Comportamiento actual (sin restricción)
→ No rompe funcionalidad existente
```

---

## 📚 Documentación Necesaria

### 1. Actualizar `docs/sistemas-del-motor/sistema-de-canales.md`

Agregar sección:

```markdown
## Filtrado de Audiencia (Audience Filtering)

### Concepto

Los canales pueden restringir no solo quién puede ESCRIBIR (via `lock`),
sino también quién puede RECIBIR/VER mensajes (via `audience`).

### Configuración

```python
"moderacion": {
    "lock": "rol(ADMIN)",       # Quién puede escribir
    "audience": "rol(ADMIN)"     # Quién puede recibir
}
```

### Comportamiento

1. **Al suscribirse** (`/activarcanal`):
   - Si hay `audience`, valida permisos
   - Si no cumple: error claro

2. **Al enviar mensaje**:
   - Filtra destinatarios según `audience`
   - Solo envía a jugadores que cumplan con el filtro

### Ejemplos de Uso

**Canal solo para administradores**:
```python
"staff": {
    "audience": "rol(ADMIN)"
}
```

**Canal para VIPs o admins**:
```python
"premium": {
    "audience": "tiene_objeto(pase_premium) or rol(ADMIN)"
}
```

**Canal para jugadores con nivel alto**:
```python
"veteranos": {
    "audience": "tiene_objeto(insignia_veterano)"
}
```

### Ventajas

- ✅ Privacidad garantizada (validación en tiempo real)
- ✅ Maneja cambios de rol dinámicamente
- ✅ Reutiliza sistema de locks (consistencia)
- ✅ Flexible (cualquier expresión de lock)
```

---

### 2. Actualizar `CLAUDE.md`

Agregar a "Sistemas Clave":

```markdown
### 15. Sistema de Filtrado de Audiencia en Canales

Los canales pueden filtrar destinatarios usando el campo `audience`:

```python
# game_data/channel_prototypes.py
"moderacion": {
    "lock": "rol(ADMIN)",      # Quién escribe
    "audience": "rol(ADMIN)"    # Quién recibe
}
```

**Implementación**:
- Validación en suscripción (UX, prevención)
- Validación en broadcast (privacidad, tiempo real)
- Reutiliza `permission_service.can_execute()`

**Uso**:
- Sin `audience` → Sin restricción (comportamiento actual)
- Con `audience` → Filtra destinatarios según lock expression
```

---

## 🚨 Consideraciones de Seguridad

1. **Privacidad Garantizada**:
   - La validación en broadcast es la capa crítica
   - Incluso si hay datos inconsistentes, no se filtra información

2. **Performance**:
   - Validación de locks es O(1) por personaje
   - Overhead mínimo (AST evaluator es rápido)
   - Ya se itera sobre todos los personajes (sin costo adicional)

3. **Backward Compatibility**:
   - Canales sin `audience` → comportamiento actual
   - No rompe funcionalidad existente
   - Migración gradual posible

4. **Fail-Safe**:
   - Si evaluación de lock falla → no envía mensaje (seguro)
   - Logs detallados para debugging

---

## 💡 Extensiones Futuras (Opcional)

### 1. Comando `/infocanal <nombre>`

Mostrar información completa de un canal:
```
🛡️ MODERACIÓN

Descripción: Canal privado para administradores

Lock (escribir): rol(ADMIN)
Audience (recibir): rol(ADMIN)

Estado: 🔓 Tienes acceso
Suscripción: ✅ Activado
```

### 2. Auditoría de Canales

Comando `/auditarcanales` (SUPERADMIN):
- Listar jugadores suscritos a cada canal
- Detectar suscripciones incorrectas (no cumplen audience)
- Limpiar automáticamente

### 3. Canales Dinámicos con Audience

Permitir que canales creados por jugadores (`/crearcanal`) tengan filtro de audiencia:
```
/crearcanal gremio_guerreros "Canal del gremio" "tiene_objeto(insignia_guerrero)"
```

---

## 📊 Resumen Ejecutivo

**Problema**: Canales no filtran destinatarios, solo quién puede escribir.

**Solución**: Campo `audience` en prototipos con sintaxis de locks.

**Implementación**: Doble validación (suscripción + broadcast).

**Beneficios**:
- ✅ Privacidad garantizada
- ✅ Reutiliza sistema existente
- ✅ Flexible y expresivo
- ✅ Backward compatible

**Esfuerzo**: ~3-4 horas (implementación + tests + documentación)

**Prioridad**: Alta (afecta privacidad de canal "moderacion" existente)

---

## 🔄 Commit en Git

Una vez completada la implementación, crear commit con los cambios:

### Archivos a incluir en el commit:

```bash
git add game_data/channel_prototypes.py
git add src/services/channel_service.py
git add commands/player/channels.py
git add docs/sistemas-del-motor/sistema-de-canales.md
git add CLAUDE.md
```

### Mensaje de commit sugerido:

```
Feature: Sistema de filtrado de audiencia para canales

Implementa doble validación (suscripción + broadcast) para controlar
no solo quién puede escribir en canales, sino quién puede recibir mensajes.

Características:
- Campo "audience" en prototipos de canales con sintaxis de locks
- Validación en suscripción: previene suscripciones incorrectas
- Validación en broadcast: garantiza privacidad en tiempo real
- Maneja cambios de rol dinámicamente
- Indicadores visuales en /canales (🔒/🔓)

Archivos modificados:
- game_data/channel_prototypes.py: Agregado campo audience
- src/services/channel_service.py: Doble validación implementada
- commands/player/channels.py: Indicadores visuales de restricción
- docs/sistemas-del-motor/sistema-de-canales.md: Nueva sección
- CLAUDE.md: Sistema #15 agregado

Tests:
- ✅ Jugador sin permiso no puede suscribirse a canales restringidos
- ✅ Admin degradado deja de recibir mensajes automáticamente
- ✅ Backward compatible con canales sin audience
- ✅ Lógica compleja (OR, AND) funciona correctamente

Fixes: Fuga de privacidad en canal "moderacion"

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

**Fecha de especificación**: 2025-01-11
**Autor**: Análisis colaborativo Claude + Usuario
**Estado**: Pendiente de implementación
