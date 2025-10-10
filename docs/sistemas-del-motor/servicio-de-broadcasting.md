---
título: "Servicio de Broadcasting"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-10"
autor: "Proyecto Runegram"
etiquetas: ["broadcasting", "mensajería", "comunicación", "telegram"]
documentos_relacionados:
  - "sistemas-sociales.md"
  - "presencia-en-linea.md"
  - "sistema-de-canales.md"
referencias_código:
  - "src/services/broadcaster_service.py"
estado: "actual"
---

# Servicio de Broadcasting

El **Broadcaster Service** (`broadcaster_service.py`) es la capa de abstracción centralizada para todo el envío de mensajes desde el juego hacia los jugadores a través de Telegram. Actúa como intermediario único entre la lógica del juego y la API del bot.

## Filosofía

En lugar de que cada comando, sistema o servicio llame directamente a `bot.send_message()`, todo el envío de mensajes pasa por este servicio centralizado. Esto proporciona:

### 1. **Consistencia**
- Todos los mensajes usan el mismo formato y comportamiento
- Parse mode estandarizado (HTML por defecto)
- Manejo uniforme de mensajes

### 2. **Manejo de Errores Unificado**
- La lógica para gestionar errores de Telegram está en un solo lugar
- Manejo robusto de usuarios que bloquean el bot
- Logging centralizado de problemas de envío
- **El juego nunca se detiene** si falla el envío a un jugador

### 3. **Desacoplamiento**
- El resto del código no necesita saber detalles de Telegram
- Fácil cambiar implementación (ej: agregar rate limiting)
- Testeo simplificado con mocks del servicio

### 4. **Filtrado Automático de Jugadores Offline**
- `send_message_to_room()` automáticamente **excluye jugadores desconectados**
- Implementa la política de "jugadores offline = ausentes del mundo"
- Ver: [Política de Jugadores Desconectados](sistemas-sociales.md#política-de-jugadores-desconectados)

## API del Servicio

### `send_message_to_character(character, message_text, parse_mode="HTML")`

Envía un mensaje a un personaje específico.

**Parámetros:**
- `character` (Character): Instancia del modelo Character (debe tener `.account` precargado)
- `message_text` (str): Contenido del mensaje a enviar
- `parse_mode` (str, opcional): Modo de parseo de Telegram (default: "HTML")

**Uso:**
```python
from src.services import broadcaster_service

await broadcaster_service.send_message_to_character(
    character=character,
    message_text="<b>¡Has encontrado un tesoro!</b>",
    parse_mode="HTML"
)
```

**Comportamiento:**
- Valida que el personaje y su cuenta existan
- Intenta enviar el mensaje vía `bot.send_message()`
- Si falla (ej: usuario bloqueó el bot), loggea el error **sin lanzar excepción**
- **El juego continúa** incluso si el envío falla

**Importante:**
- ⚠️ **Siempre precarga `.account`**: El objeto `character` debe tener su relación `.account` cargada (usa `selectinload(Character.account)` en la query).

---

### `send_message_to_room(session, room_id, message_text, exclude_character_id=None, parse_mode="HTML")`

Envía un mensaje a todos los personajes **activamente jugando (online)** en una sala específica.

**Parámetros:**
- `session` (AsyncSession): Sesión de base de datos activa
- `room_id` (int): ID de la sala objetivo
- `message_text` (str): Contenido del mensaje a enviar
- `exclude_character_id` (int, opcional): ID de personaje a excluir (útil para no notificar al actor de una acción)
- `parse_mode` (str, opcional): Modo de parseo de Telegram (default: "HTML")

**Uso:**
```python
from src.services import broadcaster_service

# Notificar a toda la sala
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=character.room_id,
    message_text="<i>Un trueno retumba en la distancia.</i>"
)

# Notificar a sala excluyendo al personaje que realizó la acción
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=character.room_id,
    message_text=f"<i>{character.name} coge una espada del suelo.</i>",
    exclude_character_id=character.id  # No notificar al que cogió el objeto
)
```

**Comportamiento:**
1. Obtiene todos los personajes en la sala (con `.account` precargado automáticamente)
2. **Filtra jugadores desconectados** usando `online_service.is_character_online()`
3. Excluye el personaje especificado en `exclude_character_id` (si se proporcionó)
4. Envía el mensaje a cada personaje restante usando `send_message_to_character()`

**Importante:**
- ✅ **Filtrado automático de offline**: Solo los jugadores activos reciben el mensaje
- ✅ **No requiere precarga manual**: La función carga `.account` automáticamente
- ✅ **Nunca falla completamente**: Si un envío falla, continúa con los demás jugadores

---

## Casos de Uso Comunes

### 1. Notificaciones de Acciones Sociales

Cuando un jugador realiza una acción visible (movimiento, coger objeto, etc.), notificar a la sala:

```python
# Jugador coge objeto del suelo
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=character.room_id,
    message_text=f"<i>{character.name} coge {item.name} del suelo.</i>",
    exclude_character_id=character.id
)
```

**Formato:** Mensajes en cursiva (`<i>`) para distinguirlos de texto del sistema.

---

### 2. Eventos del Mundo

Eventos automáticos que afectan a toda una sala:

```python
# Tick script que causa un evento en la sala
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=room.id,
    message_text="<i>Las antorchas de la sala parpadean misteriosamente.</i>"
)
```

---

### 3. Mensajes Privados Contextuales

Enviar información privada a un jugador específico:

```python
# Resultado de examinar un objeto con información secreta
await broadcaster_service.send_message_to_character(
    character=character,
    message_text="<i>Notas una inscripción oculta en la pared...</i>"
)
```

---

### 4. Movimiento Entre Salas

Notificar salida de sala origen y llegada a sala destino:

```python
# Sala de origen
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=origin_room_id,
    message_text=f"<i>{character.name} se marcha hacia el {direction}.</i>",
    exclude_character_id=character.id
)

# Sala de destino
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=destination_room_id,
    message_text=f"<i>{character.name} llega desde el {opposite_direction}.</i>",
    exclude_character_id=character.id
)
```

**Nota:** El filtrado de offline es automático; solo los jugadores activos en cada sala reciben las notificaciones.

---

## Integración con Otros Sistemas

### Sistema de Presencia (Online/Offline)

El broadcaster service se integra estrechamente con `online_service`:

```python
# En send_message_to_room()
if not await online_service.is_character_online(char.id):
    logging.debug(f"BROADCASTER: Saltando mensaje a {char.name} porque está desconectado")
    continue
```

**Resultado:** Los jugadores desconectados **nunca** reciben notificaciones de eventos del mundo.

Ver: [Sistema de Presencia en Línea](presencia-en-linea.md)

---

### Sistema de Canales

Los canales estáticos y dinámicos usan el broadcaster para enviar mensajes:

```python
# En channel_service.send_message_to_channel()
for subscriber in active_subscribers:
    await broadcaster_service.send_message_to_character(
        character=subscriber,
        message_text=formatted_message
    )
```

Ver: [Sistema de Canales](sistema-de-canales.md)

---

### Sistema de Narrativa

El servicio de narrativa genera mensajes evocativos que se envían a través del broadcaster:

```python
narrative_message = narrative_service.get_random_narrative(
    "item_spawn",
    item_name=item.name
)

await broadcaster_service.send_message_to_room(
    session=session,
    room_id=room_id,
    message_text=narrative_message
)
```

Ver: [Sistema de Narrativa](sistema-de-narrativa.md)

---

## Manejo de Errores

### Errores de Telegram

Los errores más comunes al enviar mensajes:

**1. Usuario bloqueó el bot**
```python
# Exception: Forbidden: bot was blocked by the user
```
**Comportamiento:** Se loggea el error, pero el juego continúa normalmente.

**2. Usuario no existe**
```python
# Exception: Bad Request: chat not found
```
**Comportamiento:** Se loggea el error. Esto puede indicar datos corruptos en la BD.

**3. Rate limiting de Telegram**
```python
# Exception: Too Many Requests: retry after X
```
**Comportamiento:** Actualmente se loggea. **Mejora futura:** Implementar retry con backoff.

### Logging

Todos los errores se loggean con contexto completo:

```python
logging.exception(
    f"BROADCASTER: No se pudo enviar mensaje a {character.name} (ID: {character.id})"
)
```

**Nivel de logging:**
- `INFO`: Envíos exitosos (puede deshabilitarse en producción)
- `DEBUG`: Jugadores offline filtrados
- `WARNING`: Intentos de envío a objetos nulos
- `ERROR`: Relaciones no cargadas (`.account` faltante)
- `EXCEPTION`: Fallos al enviar vía Telegram API

---

## Mejores Prácticas

### 1. Siempre Usar el Broadcaster

❌ **Incorrecto:**
```python
from src.bot.bot import bot

await bot.send_message(
    chat_id=character.account.telegram_id,
    text="Mensaje"
)
```

✅ **Correcto:**
```python
from src.services import broadcaster_service

await broadcaster_service.send_message_to_character(
    character=character,
    message_text="Mensaje"
)
```

**Razón:** Usar el broadcaster asegura manejo de errores, logging y consistencia.

---

### 2. Precargar Relaciones para `send_message_to_character()`

❌ **Incorrecto:**
```python
character = await session.get(Character, character_id)
await broadcaster_service.send_message_to_character(character, "Mensaje")
# ERROR: character.account no está cargado
```

✅ **Correcto:**
```python
result = await session.execute(
    select(Character)
    .where(Character.id == character_id)
    .options(selectinload(Character.account))
)
character = result.scalar_one()
await broadcaster_service.send_message_to_character(character, "Mensaje")
```

**Razón:** `send_message_to_character()` requiere `.account` cargado. `send_message_to_room()` lo hace automáticamente.

---

### 3. Usar `exclude_character_id` para Evitar Redundancia

❌ **Incorrecto:**
```python
# Jugador recibe feedback directo
await message.answer("Coges la espada.")

# Y también recibe la notificación social (redundante)
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=character.room_id,
    message_text=f"<i>{character.name} coge la espada.</i>"
    # No excluye al jugador que realizó la acción
)
```

✅ **Correcto:**
```python
# Jugador recibe feedback directo
await message.answer("Coges la espada.")

# Solo los demás jugadores reciben la notificación
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=character.room_id,
    message_text=f"<i>{character.name} coge la espada.</i>",
    exclude_character_id=character.id  # ← Excluye al actor
)
```

**Razón:** El jugador que realiza la acción ya recibe feedback directo; no necesita ver la notificación social.

---

### 4. Formato Consistente de Mensajes Sociales

Todos los mensajes sociales (acciones visibles) deben usar cursiva:

```python
await broadcaster_service.send_message_to_room(
    session=session,
    room_id=room_id,
    message_text=f"<i>{character.name} realiza una acción.</i>"
)
```

**Regla:** Usar `<i>` para distinguir mensajes sociales de feedback directo o texto del sistema.

Ver: [Guía de Estilo de Salida](../creacion-de-contenido/guia-de-estilo-de-salida.md)

---

## Limitaciones Conocidas

### 1. Sin Rate Limiting Implementado

**Problema:** Envíos masivos (ej: 100+ jugadores en una sala) pueden triggerar límites de Telegram.

**Solución futura:** Implementar cola de mensajes con rate limiting.

---

### 2. Sin Retry Automático

**Problema:** Si Telegram está temporalmente caído, los mensajes se pierden.

**Solución futura:** Sistema de retry con exponential backoff para errores temporales.

---

### 3. Sin Priorización de Mensajes

**Problema:** Mensajes críticos (ej: "estás bajo ataque") no tienen prioridad sobre mensajes ambientales.

**Solución futura:** Sistema de colas con prioridad.

---

## Ver También

- [Sistemas Sociales](sistemas-sociales.md) - Uso del broadcasting en interacciones sociales
- [Sistema de Presencia](presencia-en-linea.md) - Filtrado de jugadores offline
- [Sistema de Canales](sistema-de-canales.md) - Comunicación global usando broadcaster
- [Sistema de Narrativa](sistema-de-narrativa.md) - Mensajes evocativos enviados vía broadcaster

---

**Versión:** 1.0
**Última actualización:** 2025-10-10
