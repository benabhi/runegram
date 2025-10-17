---
título: "Sistema de Baneos y Apelaciones"
categoría: "Sistemas del Motor"
versión: "1.2"
última_actualización: "2025-01-11"
autor: "Proyecto Runegram"
etiquetas: ["baneos", "moderacion", "apelaciones", "administracion", "configuracion"]
documentos_relacionados:
  - "sistema-de-permisos.md"
  - "sistema-de-canales.md"
  - "../arquitectura/configuracion.md"
  - "../guia-de-administracion/comandos-de-administracion.md"
  - "../referencia/referencia-de-comandos.md"
referencias_código:
  - "src/services/ban_service.py"
  - "commands/admin/ban_management.py"
  - "commands/player/appeal.py"
  - "src/handlers/player/dispatcher.py"
  - "game_data/channel_prototypes.py"
  - "gameconfig.toml"
  - "src/config.py"
estado: "actual"
importancia: "alta"
audiencia: "desarrollador"
---

# Sistema de Baneos y Apelaciones

Sistema completo de moderación que permite a los administradores banear cuentas de forma temporal o permanente, con sistema de apelaciones para jugadores baneados.

## 🎯 Visión General

El sistema de baneos permite:
- **Baneos temporales**: Con fecha de expiración automática
- **Baneos permanentes**: Sin fecha de expiración
- **Apelaciones**: Una oportunidad por cuenta para explicar su caso
- **Auditoría completa**: Registro de quién, cuándo y por qué se baneó
- **Verificación automática**: Expiración automática de baneos temporales

---

## 🏗️ Arquitectura del Sistema

### Servicio Principal

**Archivo**: `src/services/ban_service.py`

**Funciones públicas**:
1. `is_account_banned(session, account)` - Verifica estado de ban (considera expiración)
2. `ban_account(session, character, reason, banned_by_account_id, expires_at)` - Aplica ban
3. `unban_account(session, character)` - Quita ban
4. `submit_appeal(session, account, appeal_text)` - Registra apelación
5. `get_banned_accounts(session, page, per_page)` - Lista paginada
6. `get_account_ban_info(session, character)` - Info completa de ban
7. `check_and_expire_bans(session)` - Expira baneos temporales (batch)

---

## 🗄️ Modelo de Datos

**Campos agregados al modelo `Account`**:

```python
is_banned: bool = False                    # Si está baneada
ban_reason: Optional[str]                  # Razón del ban (max 500 chars)
banned_at: Optional[datetime]              # Cuándo se baneó
banned_by_account_id: Optional[int]        # Quién aplicó el ban
ban_expires_at: Optional[datetime]         # Expiración (None = permanente)

has_appealed: bool = False                 # Si ya apeló
appeal_text: Optional[str]                 # Texto de apelación (max 1000 chars)
appealed_at: Optional[datetime]            # Cuándo apeló

# Relación
banned_by: relationship("Account")         # Cuenta del admin que baneó
```

---

## 🔒 Lógica de Negocio

### 1. Verificación de Ban

```python
async def is_account_banned(session, account) -> bool:
    if not account.is_banned:
        return False

    # Verificar expiración automática
    if account.ban_expires_at:
        if datetime.utcnow() >= account.ban_expires_at:
            await _auto_unban_expired(session, account)
            return False

    return True
```

**Características**:
- ✅ Verifica expiración automáticamente
- ✅ Desbanea automáticamente si ban temporal expiró
- ✅ Fail-safe en caso de error (asume NO baneado)

---

### 2. Aplicar Ban

```python
await ban_account(
    session=session,
    character=target_character,
    reason="Spam en canales globales",
    banned_by_account_id=admin_account.id,
    expires_at=datetime.utcnow() + timedelta(days=7)  # Temporal
)
```

**Validaciones**:
- ❌ Error si cuenta ya está baneada
- ❌ Error si razón está vacía o excede 500 caracteres
- ✅ Registra timestamp y admin responsable
- ✅ Logging exhaustivo para auditoría

**Ban permanente**: Pasar `expires_at=None`

---

### 3. Sistema de Apelaciones

```python
await submit_appeal(
    session=session,
    account=banned_account,
    appeal_text="Explicación del jugador..."
)
```

**Restricciones**:
- ❌ Solo una apelación por cuenta (has_appealed)
- ❌ Solo si cuenta está baneada
- ❌ Máximo 1000 caracteres
- ✅ Se mantiene historial incluso después de desbanear

---

### 4. Expiración Automática de Baneos

```python
# Llamar periódicamente (ej: cada 1 hora mediante scheduler)
expired_count = await check_and_expire_bans(session)
```

**Comportamiento**:
- Busca todos los baneos temporales expirados
- Los desbanea en batch
- Retorna cantidad de cuentas desbaneadas
- Logging de cada operación

---

## 🎮 Comandos Implementados

### Comandos de Admin

#### `/banear <nombre> [días] <razón>`
**Aliases**: Ninguno
**Permiso**: `ADMIN`

**Uso**:
```
/banear Gandalf 7 Spam en canales globales
/banear Frodo Uso de exploits graves
```

**Comportamiento**:
- Si se especifica días → ban temporal
- Si NO se especifica días → ban permanente
- Razón es obligatoria
- Se notifica al admin del éxito

---

#### `/desbanear <nombre>`
**Aliases**: Ninguno
**Permiso**: `ADMIN`

**Uso**:
```
/desbanear Gandalf
```

**Comportamiento**:
- Quita el ban completamente
- **Resetea campos de apelación** (has_appealed, appeal_text, appealed_at)
- Permite que el jugador pueda apelar de nuevo si es baneado en el futuro
- Se notifica al admin del éxito

---

#### `/listabaneados [página]`
**Aliases**: Ninguno
**Permiso**: `ADMIN`

**Uso**:
```
/listabaneados
/listabaneados 2
```

**Comportamiento**:
- Lista paginada (30 por página)
- Muestra: nombre, tipo de ban, razón, fecha, admin
- Indica si hay apelación pendiente
- Ordena por fecha de ban (más recientes primero)

---

#### `/verapelacion <nombre>`
**Aliases**: Ninguno
**Permiso**: `ADMIN`

**Uso**:
```
/verapelacion Gandalf
```

**Comportamiento**:
- Muestra apelación completa del jugador
- Muestra info del ban original
- Indica si no hay apelación

---

### Comandos de Jugador

#### `/apelar <explicación>`
**Aliases**: Ninguno
**Permiso**: Ninguno (solo jugadores baneados)

**Uso**:
```
/apelar Fui víctima de un hack. Mi hermano usó mi cuenta sin permiso y cometió spam.
```

**Comportamiento**:
- Solo disponible para jugadores baneados
- Solo se puede enviar UNA vez (hasta que sea desbaneado)
- Máximo 1000 caracteres
- Se notifica al jugador del éxito
- **Notifica a administradores** según configuración (ver [Configuración](#⚙️-configuración))

---

## 🚫 Integración con Dispatcher

**Archivo**: `src/handlers/player/dispatcher.py`

**Función**: `main_command_dispatcher()`

```python
# Verificar ban ANTES de ejecutar cualquier comando
if await ban_service.is_account_banned(session, account):
    # Permitir SOLO el comando /apelar
    if command_obj.names[0] != "apelar":
        ban_info = await ban_service.get_account_ban_info(session, character)
        # Mostrar mensaje de ban con info
        await message.answer(...)
        return
```

**Comportamiento**:
- ✅ Bloquea TODOS los comandos para usuarios baneados
- ✅ Excepto `/apelar` (permitido para que puedan apelar)
- ✅ Muestra mensaje claro con razón del ban
- ✅ Indica si es temporal y cuándo expira
- ✅ Sugiere `/apelar` si no ha apelado

---

## 🔍 Casos de Uso

### Caso 1: Ban Temporal por Spam

**Administrador**:
```
/banear Pippin 3 Spam repetido en canal Novato
```

**Jugador Pippin**:
- Intenta usar cualquier comando → Ve mensaje de ban
- Puede usar `/apelar` UNA vez
- Después de 3 días → Ban expira automáticamente

---

### Caso 2: Ban Permanente por Exploit

**Administrador**:
```
/banear Saruman Uso de exploit de duplicación de items
```

**Jugador Saruman**:
- Ban permanente (sin expiración)
- Puede apelar con `/apelar`
- Solo un admin puede desbanear

---

### Caso 3: Revisión de Apelación

**Administrador**:
```
/listabaneados           # Ve que Gandalf tiene apelación pendiente (🔔)
/verapelacion Gandalf    # Lee la apelación
/desbanear Gandalf       # Decide desbanear
```

---

## ⚙️ Configuración

### Configuración en `gameconfig.toml`

```toml
[moderation]
# Canal donde se envían notificaciones de apelaciones de ban
# Si se deja vacío (""), las notificaciones se envían directamente a todos los admins
# Debe ser una key válida de CHANNEL_PROTOTYPES (ej: "moderacion", "sistema")
ban_appeal_channel = "moderacion"
```

**Opciones de `ban_appeal_channel`**:

1. **Valor configurado con canal válido** (ej: `"moderacion"`):
   - Las notificaciones de apelaciones se envían al canal especificado
   - Solo los administradores suscritos a ese canal recibirán las notificaciones
   - Recomendado para mantener la privacidad de las apelaciones

2. **Valor vacío** (`""`):
   - Las notificaciones se envían como **mensaje directo** a todos los administradores (ADMIN y SUPERADMIN)
   - Asegura que todos los admins reciban la notificación
   - Útil si no hay canal de moderación configurado

**Canal de Moderación Recomendado**:

El proyecto incluye un canal `"moderacion"` preconfigurado en `game_data/channel_prototypes.py`:

```python
"moderacion": {
    "name": "Moderación",
    "icon": "🛡️",
    "description": "Canal privado para administradores (apelaciones, moderación).",
    "type": "CHAT",
    "default_on": False,
    "lock": "rol(ADMIN)",       # Solo ADMINS y SUPERADMINS pueden escribir
    "audience": "rol(ADMIN)"    # Se activa automáticamente para admins nuevos
}
```

**Nota de activación automática**:

El canal "moderacion" se activa **automáticamente** para administradores nuevos gracias al campo `audience: "rol(ADMIN)"`. Los administradores existentes (antes de esta característica) deben activarlo manualmente con:

```
/activarcanal moderacion
```

### Límites Configurables

Todos los límites del sistema de baneos son configurables en `gameconfig.toml` bajo la sección `[moderation]`:

```toml
[moderation]
ban_appeal_channel = "moderacion"
ban_reason_max_length = 500
appeal_max_length = 1000
appeal_preview_length = 100
banned_accounts_per_page = 10
```

**Campos configurables:**

| Campo | Default | Descripción |
|-------|---------|-------------|
| `ban_reason_max_length` | 500 | Máximo de caracteres para la razón del ban |
| `appeal_max_length` | 1000 | Máximo de caracteres para el texto de apelación |
| `appeal_preview_length` | 100 | Caracteres mostrados en vista previa de apelaciones |
| `banned_accounts_per_page` | 10 | Número de cuentas por página en `/listabaneados` |

**Uso en código:**
```python
from src.config import settings

# Validar longitud de razón
if len(reason) > settings.moderation_ban_reason_max_length:
    await message.answer(f"❌ La razón no puede exceder {settings.moderation_ban_reason_max_length} caracteres.")

# Validar longitud de apelación
if len(appeal_text) > settings.moderation_appeal_max_length:
    await message.answer(f"❌ La apelación no puede exceder {settings.moderation_appeal_max_length} caracteres.")

# Paginación
per_page = settings.moderation_banned_accounts_per_page
```

Para modificar estos valores, edita `gameconfig.toml` y reinicia el bot. Ver [documentación de configuración](../arquitectura/configuracion.md#sección-moderation) para más detalles.

---

## 📊 Auditoría y Logging

Todas las operaciones generan logs detallados:

```python
logging.info(
    f"Ban temporal aplicado a cuenta {account.id} (personaje: {character.name}). "
    f"Razón: '{reason}'. Aplicado por cuenta {banned_by_account_id}. (expira: {expires_at})"
)
```

**Logs generados**:
- ✅ Aplicación de ban (temporal/permanente)
- ✅ Desbaneo manual
- ✅ Desbaneo automático por expiración
- ✅ Apelaciones registradas
- ✅ Errores en operaciones

---

## 🚨 Consideraciones de Seguridad

### Prevención de Abuso

1. **Una apelación por cuenta**: `has_appealed` impide spam de apelaciones
2. **Razón obligatoria**: Todo ban debe tener justificación
3. **Auditoría completa**: Se registra quién y cuándo baneó
4. **Validaciones robustas**: Límites de caracteres, estado de cuenta, etc.

### Fail-Safe

- Si `is_account_banned()` falla → Asume NO baneado (permite jugar)
- Evita bloquear usuarios por errores técnicos

---

## 🔮 Futuras Mejoras

### Propuestas

1. **Sistema de advertencias** (warnings) antes de ban
2. **Historial de baneos** en tabla separada (múltiples baneos)
3. **Baneos por IP** (además de cuenta)
4. **Auto-moderación** (detección automática de spam)
5. **Panel web de moderación** para admins
6. **Escalado de sanciones** (warn → 1 día → 7 días → permanente)
7. ~~**Configurar límites** (razón, apelación) en gameconfig.toml~~ ✅ **IMPLEMENTADO en v1.2**

---

## 📚 Referencias

**Código fuente**:
- `src/services/ban_service.py` - Lógica de negocio
- `commands/admin/ban_management.py` - Comandos de admin
- `commands/player/appeal.py` - Comando de apelación
- `src/handlers/player/dispatcher.py` - Integración con dispatcher
- `src/models/account.py` - Modelo de datos

**Documentación relacionada**:
- [Sistema de Permisos](sistema-de-permisos.md)
- [Comandos de Administración](../guia-de-administracion/comandos-de-administracion.md)
- [Referencia de Comandos](../referencia/referencia-de-comandos.md)

---

## 🛠️ Para Desarrolladores

### Agregar Nuevo Tipo de Ban

1. Agregar campo al modelo `Account` en `src/models/account.py`
2. Crear migración con Alembic
3. Extender `ban_service.py` con nueva funcionalidad
4. Actualizar comandos en `commands/admin/ban_management.py`
5. **Actualizar esta documentación**

### Ejecutar Expiración Periódica

**Recomendación**: Llamar `check_and_expire_bans()` desde el sistema de scheduling cada 1 hora.

```python
# En src/services/scheduler_service.py o mediante cron scripts
@scheduler.scheduled_job('interval', hours=1, id='expire_bans')
async def expire_bans_job():
    async with get_session() as session:
        await ban_service.check_and_expire_bans(session)
```

---

## 📝 Changelog

### v1.2 (2025-01-11)
- ✅ **Límites configurables**: Migración completa de valores hardcodeados a `gameconfig.toml`
  - `ban_reason_max_length` (500)
  - `appeal_max_length` (1000)
  - `appeal_preview_length` (100)
  - `banned_accounts_per_page` (10)
- ✅ **Documentación actualizada**: Sección "Límites Configurables" con ejemplos de uso
- ✅ **Referencia cruzada**: Enlaces a documentación de configuración

### v1.1 (2025-01-11)
- ✅ **Desbaneo resetea apelación**: Ahora `/desbanear` resetea los campos de apelación, permitiendo que el jugador pueda apelar de nuevo si es baneado en el futuro
- ✅ **Canal de moderación**: Agregado canal "moderacion" en `channel_prototypes.py` con lock de ADMIN
- ✅ **Configuración de notificaciones**: Agregado `moderation.ban_appeal_channel` en `gameconfig.toml`
- ✅ **Fallback a mensajes directos**: Si no hay canal configurado, se envían mensajes directos a todos los administradores
- ✅ **Documentación de configuración**: Sección completa sobre cómo configurar notificaciones de apelaciones

### v1.0 (2025-01-11)
- ✅ Sistema completo de baneos y apelaciones implementado
- ✅ Baneos temporales y permanentes
- ✅ Sistema de apelaciones (una por cuenta)
- ✅ Comandos de admin y jugador
- ✅ Integración con dispatcher
- ✅ Auditoría completa

---

**Versión:** 1.2
**Última actualización:** 2025-01-11
**Estado:** Sistema completo y funcional con configuración centralizada
