---
título: "Sistema de Canales"
categoría: "Sistemas del Motor"
versión: "2.0"
última_actualización: "2025-01-11"
autor: "Proyecto Runegram"
etiquetas: ["canales", "comunicación", "global", "canales-dinámicos", "audience", "filtrado"]
documentos_relacionados:
  - "sistemas-del-motor/sistemas-sociales.md"
  - "sistemas-del-motor/sistema-de-comandos.md"
  - "sistemas-del-motor/sistema-de-permisos.md"
referencias_código:
  - "src/services/channel_service.py"
  - "game_data/channel_prototypes.py"
  - "commands/player/dynamic_channels.py"
  - "commands/player/channels.py"
  - "src/models/character_setting.py"
estado: "actual"
---

# Channels System

El Sistema de Canales proporciona un medio para la comunicación global entre jugadores, así como para anuncios del sistema. Está gestionado por `src/services/channel_service.py`.

## Arquitectura "Data-Driven"

*   **Prototipos de Canal (`game_data/channel_prototypes.py`):** Es la "fuente de la verdad". Define todos los canales, su nombre, icono, descripción y, lo más importante, su **tipo** y sus **permisos**.
    *   `"type": "CHAT"`: Indica al sistema que debe generar dinámicamente un comando (ej: `/novato`) para que los jugadores puedan hablar en este canal.
    *   `"lock": "rol(ADMIN)"`: Un `lock string` opcional que se asigna al comando generado, restringiendo quién puede **escribir** en el canal.
    *   `"audience": "rol(ADMIN)"`: Un `lock string` opcional que determina quién puede **recibir/ver** mensajes del canal. Ver sección [Filtrado de Audiencia](#filtrado-de-audiencia).

*   **Configuración de Usuario (`CharacterSetting`):** La suscripción de un jugador a un canal se almacena en la base de datos, en la columna `active_channels` de su tabla de `character_settings`. Esto hace que sus preferencias sean persistentes.

## Flujo de Funcionamiento

*   **Hablar en un Canal (ej: `/novato ¡hola!`):**
    1.  El `dispatcher` identifica el comando `/novato`, que fue generado dinámicamente por el módulo `dynamic_channels`.
    2.  Se comprueban los `locks` del comando (leídos desde el prototipo del canal) para verificar que el jugador puede **escribir**.
    3.  `CmdDynamicChannel.execute()` se ejecuta. Llama a `channel_service` para comprobar si el jugador está suscrito al canal "novato".
    4.  Si está suscrito, se llama a `channel_service.broadcast_to_channel()`.
    5.  Esta función recupera de la base de datos a **todos los personajes del juego**.
    6.  Itera sobre ellos, y para cada uno, comprueba:
        *   Si tiene el canal "novato" activo en su configuración.
        *   Si el canal tiene filtro de `audience`, valida que el jugador cumpla con los permisos (usando `permission_service.can_execute()`).
    7.  Si ambas condiciones se cumplen, utiliza el `broadcaster_service` para enviarle el mensaje formateado.

*   **Gestión de Canales:**
    *   `/canales`: Lista todos los prototipos de canal y muestra si el jugador está suscrito a cada uno.
    *   `/activarcanal <nombre>` y `/desactivarcanal <nombre>`: Modifican la lista de `active_channels` en la configuración del personaje en la base de datos.

## Tipos de Canales

### Canales Estáticos

Los canales estáticos están definidos en `channel_prototypes.py` y se crean automáticamente al arrancar el bot.

**Ejemplo:**
```python
"novato": {
    "name": "Canal Novato",
    "icon": "🌱",
    "description": "Canal de ayuda para jugadores nuevos",
    "type": "CHAT",
    "lock": "",         # Todos pueden escribir
    "audience": "",     # Todos pueden recibir
}

"moderacion": {
    "name": "Canal de Moderación",
    "icon": "🛡️",
    "description": "Canal privado para administradores",
    "type": "CHAT",
    "lock": "rol(ADMIN)",      # Solo admins pueden escribir
    "audience": "rol(ADMIN)",   # Solo admins pueden recibir
}
```

### Canales Dinámicos (Futuro)

El sistema está preparado para soportar canales creados por jugadores:
- `/crearcanal <nombre>`: Crea un canal privado
- `/invitar <jugador> <canal>`: Invita a otro jugador al canal
- `/salircanal <nombre>`: Abandona un canal creado por jugador

## Comandos de Gestión

### `/canales`
Lista todos los canales disponibles y muestra el estado de suscripción.

**Ejemplo de salida:**
```
📻 CANALES DISPONIBLES

🌱 Canal Novato [ACTIVO]
   Canal de ayuda para jugadores nuevos

⚙️ Canal de Administración
   Canal privado para administradores

Para activar: /activarcanal <nombre>
Para desactivar: /desactivarcanal <nombre>
```

### `/activarcanal <nombre>`
Suscribe al jugador a un canal específico.

**Ejemplo:**
```
> /activarcanal novato
✅ Te has suscrito al canal 'novato'.
```

### `/desactivarcanal <nombre>`
Desuscribe al jugador de un canal.

**Ejemplo:**
```
> /desactivarcanal novato
✅ Te has desuscrito del canal 'novato'.
```

### Hablar en un Canal

Una vez suscrito, el jugador puede hablar usando el comando del canal:

```
> /novato Hola a todos, soy nuevo!

[🌱 Novato] Juan: Hola a todos, soy nuevo!
```

Todos los jugadores suscritos al canal recibirán el mensaje.

## Formato de Mensajes

Los mensajes de canal usan un formato específico:

```
[ICONO NOMBRE_CANAL] Jugador: Mensaje
```

**Ejemplos:**
```
[🌱 Novato] Juan: ¿Dónde encuentro la espada?
[⚙️ Admin] María: Servidor reiniciándose en 5 minutos
```

## Permisos y Locks

Los canales tienen dos tipos de restricciones mediante `lock strings`:

### Lock (Quién puede escribir)

```python
"comercio": {
    "lock": ""  # Todos pueden escribir
}

"vip": {
    "lock": "tiene_objeto(pase_vip)"  # Solo jugadores con item específico
}

"moderacion": {
    "lock": "rol(ADMIN)"  # Solo administradores
}
```

### Audience (Quién puede recibir/ver mensajes)

```python
"novato": {
    "audience": ""  # Todos los suscritos reciben mensajes
}

"moderacion": {
    "audience": "rol(ADMIN)"  # Solo admins reciben mensajes
}

"vip": {
    "audience": "tiene_objeto(pase_vip) or rol(ADMIN)"  # VIPs o admins
}
```

Para más detalles sobre el filtrado de audiencia, ver la sección [Filtrado de Audiencia](#filtrado-de-audiencia).

## Persistencia

Las preferencias de canal se guardan en la base de datos:

```python
# En CharacterSetting model
active_channels = Column(ARRAY(String), default=[], nullable=False)
```

Esto permite que:
- Las suscripciones persistan entre sesiones
- El jugador mantenga sus preferencias al reconectarse
- Se puedan consultar/modificar las suscripciones programáticamente

## Implementación Técnica

### Generar Comandos Dinámicos

```python
# En commands/player/dynamic_channels.py

def generate_channel_commands():
    """Genera comandos dinámicos para canales de tipo CHAT."""
    commands = []

    for key, proto in CHANNEL_PROTOTYPES.items():
        if proto.get("type") == "CHAT":
            cmd = CmdDynamicChannel(
                channel_key=key,
                names=[key],  # /novato, /admin, etc.
                description=proto.get("description"),
                lock=proto.get("lock", "")
            )
            commands.append(cmd)

    return commands
```

### Broadcast a Canal

```python
# En src/services/channel_service.py

async def broadcast_to_channel(
    session: AsyncSession,
    channel_key: str,
    sender_name: str,
    message: str
):
    """Envía un mensaje a todos los suscritos a un canal."""

    # Obtener prototipo del canal
    channel_proto = CHANNEL_PROTOTYPES.get(channel_key)

    # Formatear mensaje
    icon = channel_proto.get("icon", "📻")
    name = channel_proto.get("name", channel_key)
    formatted = f"[{icon} {name}] {sender_name}: {message}"

    # Obtener todos los personajes
    result = await session.execute(select(Character))
    all_characters = result.scalars().all()

    # Filtrar suscritos y enviar
    for char in all_characters:
        if channel_key in char.settings.active_channels:
            await broadcaster_service.send_message_to_character(
                char, formatted
            )
```

## Filtrado de Audiencia

El sistema de canales implementa un mecanismo de doble validación para controlar no solo quién puede **escribir** en un canal (mediante `lock`), sino también quién puede **recibir/ver** mensajes (mediante `audience`).

### Concepto

Los canales pueden tener un filtro de audiencia que determina qué jugadores pueden recibir mensajes del canal. Esto es especialmente útil para:

- **Canales privados de administración**: Garantizar que mensajes de moderación no lleguen a jugadores comunes
- **Canales VIP**: Restringir contenido exclusivo a ciertos jugadores
- **Canales de eventos especiales**: Mostrar información solo a participantes elegibles

### Configuración

El campo `audience` en los prototipos de canales acepta un `lock string` con la misma sintaxis que el campo `lock`:

```python
# game_data/channel_prototypes.py

"moderacion": {
    "name": "Moderación",
    "icon": "🛡️",
    "description": "Canal privado para administradores",
    "type": "CHAT",
    "default_on": False,
    "lock": "rol(ADMIN)",       # Quién puede escribir
    "audience": "rol(ADMIN)"     # Quién puede recibir
}
```

**Valores posibles:**
- `audience = ""` → Sin restricción (comportamiento por defecto, todos los suscritos reciben)
- `audience = "rol(ADMIN)"` → Solo administradores reciben mensajes
- `audience = "tiene_objeto(pase_vip)"` → Solo jugadores con un item específico
- `audience = "rol(ADMIN) or tiene_objeto(pase_premium)"` → Expresiones complejas

### Comportamiento

El sistema implementa **doble validación** para garantizar privacidad:

#### 1. Validación en Suscripción

Cuando un jugador intenta activar un canal con `audience` definido:

```python
# En src/services/channel_service.set_channel_status()

if activate and audience_filter:
    can_subscribe, _ = await permission_service.can_execute(
        character,
        audience_filter
    )
    if not can_subscribe:
        raise ValueError(
            "No tienes permiso para suscribirte a este canal. "
            "Este canal está restringido a ciertos jugadores."
        )
```

**Ventajas:**
- Previene suscripciones incorrectas (mejor UX)
- Feedback inmediato al jugador
- Reduce confusión ("¿Por qué no recibo mensajes?")

**Ejemplo de uso:**
```
Jugador: /activarcanal moderacion
Bot: ❌ No tienes permiso para suscribirte al canal 'Moderación'.
     Este canal está restringido a ciertos jugadores.
```

#### 2. Validación en Broadcast (Capa de Seguridad)

Cuando se envía un mensaje a un canal, se filtra dinámicamente la audiencia:

```python
# En src/services/channel_service.broadcast_to_channel()

for char in all_characters:
    # Verificar suscripción
    if not await is_channel_active(settings, channel_key):
        continue

    # Verificar permiso de audiencia
    if audience_filter:
        can_receive, _ = await permission_service.can_execute(
            char,
            audience_filter
        )
        if not can_receive:
            logging.debug(
                f"Saltando mensaje de canal '{channel_key}' a {char.name}: "
                "no cumple filtro de audiencia"
            )
            continue

    await broadcaster_service.send_message_to_character(char, message)
```

**Ventajas:**
- Privacidad garantizada en tiempo real
- Maneja cambios de rol dinámicamente
- Fail-safe: incluso si hay datos inconsistentes, no se filtra información

**Ejemplo de escenario:**
```
1. Admin A se suscribe a "moderacion"
2. Admin A es degradado a JUGADOR (cambio de rol manual)
3. Admin B escribe: /moderacion Revisando caso de spam
   → Ex-admin NO recibe el mensaje (validación en tiempo real)
```

### Indicadores Visuales

El comando `/canales` muestra indicadores para canales con restricción de audiencia:

```python
# En commands/player/channels.py

audience_filter = proto.get("audience", "")
if audience_filter:
    can_access, _ = await permission_service.can_execute(character, audience_filter)
    restriction_icon = " 🔓" if can_access else " 🔒"
```

**Ejemplo de salida:**

```
📡 ESTADO DE TUS CANALES

    - Novato (novato): ✅ Activado
      Un canal para que los nuevos aventureros pidan ayuda.

    - Sistema (sistema): ✅ Activado
      Anuncios del juego y notificaciones automáticas.

    - Moderación (moderacion): ❌ Desactivado 🔒
      Canal privado para administradores (apelaciones, moderación).
```

**Íconos:**
- 🔓 = Canal restringido al que el jugador **tiene acceso**
- 🔒 = Canal restringido al que el jugador **NO tiene acceso**
- Sin ícono = Canal sin restricciones de audiencia

### Casos de Uso

#### Canal de Moderación (Privacidad Total)

```python
"moderacion": {
    "lock": "rol(ADMIN)",
    "audience": "rol(ADMIN)"
}
```

**Comportamiento:**
- Solo admins pueden escribir (`/moderacion mensaje`)
- Solo admins reciben mensajes
- Jugadores comunes no pueden suscribirse
- Si un admin es degradado, automáticamente deja de recibir

#### Canal VIP con Admins Incluidos

```python
"vip": {
    "lock": "tiene_objeto(pase_vip) or rol(ADMIN)",
    "audience": "tiene_objeto(pase_vip) or rol(ADMIN)"
}
```

**Comportamiento:**
- Jugadores con `pase_vip` pueden escribir y recibir
- Admins también tienen acceso (moderación)
- Lógica OR permite múltiples condiciones

#### Canal de Evento Temporal

```python
"torneo": {
    "lock": "tiene_objeto(inscripcion_torneo)",
    "audience": "tiene_objeto(inscripcion_torneo) or rol(ADMIN)"
}
```

**Comportamiento:**
- Solo inscritos pueden escribir
- Inscritos y admins reciben mensajes
- Admins pueden monitorear sin participar

#### Canal Público con Moderación Restringida

```python
"comercio": {
    "lock": "",                    # Todos pueden escribir
    "audience": ""                 # Todos reciben
}

"sistema": {
    "lock": "rol(ADMIN)",          # Solo admins escriben
    "audience": ""                 # Todos reciben (anuncios públicos)
}
```

### Ventajas del Sistema

- ✅ **Privacidad garantizada**: Validación en tiempo real evita fugas de información
- ✅ **Dinámico**: Maneja cambios de rol/permisos automáticamente
- ✅ **Reutilización de arquitectura**: Usa el mismo sistema de locks (consistencia)
- ✅ **Flexible**: Cualquier expresión de lock es válida (OR, AND, NOT)
- ✅ **Backward compatible**: Canales sin `audience` funcionan como antes
- ✅ **Fail-safe**: Si la evaluación falla, no envía mensaje (comportamiento seguro)
- ✅ **Performance aceptable**: O(1) por personaje, overhead mínimo

### Consideraciones de Performance

**Pregunta:** ¿No es costoso evaluar permisos para cada jugador en cada broadcast?

**Respuesta:**
1. El sistema **ya itera** sobre todos los personajes para verificar suscripciones
2. La evaluación de locks es O(1) (AST evaluator optimizado)
3. El overhead es mínimo (~microsegundos por personaje)
4. La privacidad justifica el costo marginal
5. En la práctica, los canales restringidos tienen pocos suscritos

**Optimización implementada:**
```python
# Solo evalúa si hay filtro de audiencia
if audience_filter:  # Evita evaluación innecesaria
    can_receive, _ = await permission_service.can_execute(...)
```

### Debugging y Logs

El sistema incluye logging detallado para debugging:

```python
logging.debug(
    f"Saltando mensaje de canal '{channel_key}' a {char.name}: "
    "no cumple filtro de audiencia"
)
```

Esto permite:
- Identificar por qué un jugador no recibe mensajes
- Auditar comportamiento del filtro
- Detectar configuraciones incorrectas

### Extensiones Futuras

Posibles mejoras al sistema de filtrado de audiencia:

#### Comando `/infocanal <nombre>`

Mostrar información detallada de un canal:

```
🛡️ MODERACIÓN

Descripción: Canal privado para administradores

Permisos:
- Escribir (lock): rol(ADMIN)
- Recibir (audience): rol(ADMIN)

Tu estado:
- Acceso: 🔒 No tienes permiso
- Suscripción: ❌ No estás suscrito
```

#### Auditoría de Suscripciones

Comando `/auditarcanales` (SUPERADMIN):
- Listar jugadores suscritos a cada canal
- Detectar suscripciones inconsistentes (no cumplen `audience`)
- Opción de limpiar automáticamente

#### Canales Dinámicos con Audience

Permitir que canales creados por jugadores tengan filtro de audiencia:

```
/crearcanal gremio_guerreros "Canal del gremio" "tiene_objeto(insignia_guerrero)"
```

## Otras Extensiones Futuras

### Canales Privados/Personales

```python
# Futuro: crear canales privados por jugadores
/crearcanal mi_grupo
/invitar Juan mi_grupo
/invitar María mi_grupo
```

### Moderación de Canales

```python
# Futuro: moderación avanzada
/mutear <jugador> <canal>
/expulsar <jugador> <canal>
```

### Historial de Canales

```python
# Futuro: ver mensajes anteriores
/historial novato
```

## Ver También

- [Sistema de Permisos](sistema-de-permisos.md) - Evaluación de locks y permisos
- [Sistemas Sociales](sistemas-sociales.md) - Interacción entre jugadores
- [Sistema de Comandos](sistema-de-comandos.md) - Generación dinámica de comandos
- [Broadcaster Service](broadcaster-service.md) - Envío de mensajes
- [Sistema de Baneos](sistema-de-baneos.md) - Moderación y restricciones de acceso
