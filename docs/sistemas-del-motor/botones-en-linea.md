---
título: "Sistema de Botones Inline"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["telegram", "botones", "fsm", "ux", "callbacks"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-comandos.md"
  - "creacion-de-contenido/guia-de-estilo-de-salida.md"
referencias_código:
  - "src/handlers/callbacks.py"
  - "src/utils/inline_keyboards.py"
  - "run.py"
estado: "actual"
---

# Inline Buttons System

El sistema de **botones inline** de Runegram permite a los jugadores interactuar con el juego mediante botones en lugar de comandos de texto. Esto mejora significativamente la experiencia de usuario en dispositivos móviles, reduciendo la necesidad de escribir comandos largos.

## Características Implementadas

- ✅ **Botón de creación de personaje** con flujo FSM
- ✅ **Botones de navegación** en salas (Norte, Sur, Este, Oeste, etc.)
- ✅ **Sistema de callback routing** extensible y escalable
- ✅ **Soporte para FSM** (multi-step conversations)
- ✅ **Callback data estructurado** y parseable

## Filosofía de Diseño

Este sistema fue diseñado pensando en:

- **Escalabilidad**: Fácil agregar nuevos tipos de botones
- **Mantenibilidad**: Código limpio y bien organizado
- **Robustez**: Manejo de errores y validaciones
- **Futuro**: Preparado para teclado dinámico completo (próximamente)

## Arquitectura del Sistema

### Componentes Principales

```
Jugador en Telegram
        ↓
   Presiona botón
        ↓
src/handlers/callbacks.py
   callback_query_router()
   ├→ parse_callback_data()
   └→ CALLBACK_HANDLERS[action]
        ↓
Handlers Específicos
   • handle_character_creation()
   • handle_movement()
   • handle_refresh()
        ↓
src/utils/inline_keyboards.py
   • create_callback_data()
   • parse_callback_data()
   • create_*_keyboard()
```

### Flujo de Ejecución

1. **Jugador presiona botón** → Telegram envía `CallbackQuery`
2. **callback_query_router()** intercepta el callback
3. **parse_callback_data()** extrae acción y parámetros
4. **CALLBACK_HANDLERS** busca el handler correspondiente
5. **Handler específico** ejecuta la lógica (mover, crear personaje, etc.)
6. **Respuesta al jugador** vía `callback.answer()` o editando mensaje

## Formato de Callback Data

### Estructura

```
"action:param1=value1:param2=value2:param3=value3"
```

### Limitación de Telegram

**Importante**: Telegram limita `callback_data` a **64 bytes**. Mantén los nombres de parámetros y valores concisos.

### Ejemplos

```python
# Movimiento
"move:direction=norte"
"move:direction=sur"

# Creación de personaje
"create_char:step=start"

# Actualizar sala
"refresh:context=room"

# Uso de item (futuro)
"use_item:item_id=123"
```

### Funciones de Callback Data

#### `create_callback_data(action, **params)`

Crea una cadena de callback_data estructurada.

```python
from src.utils.inline_keyboards import create_callback_data

callback_data = create_callback_data("move", direction="norte")
# Resultado: "move:direction=norte"
```

#### `parse_callback_data(callback_data)`

Parsea un string de callback_data en un diccionario.

```python
from src.utils.inline_keyboards import parse_callback_data

callback_info = parse_callback_data("move:direction=norte")
# Resultado: {'action': 'move', 'params': {'direction': 'norte'}}
```

## Uso de FSM (Finite State Machine)

### ¿Qué es FSM?

FSM permite crear **conversaciones multi-paso** donde el bot espera respuestas específicas del usuario en estados específicos. Es ideal para flujos complejos como:

- Creación de personaje (solicitar nombre → validar → confirmar)
- Compra de items (seleccionar item → confirmar cantidad → confirmar compra)
- Configuración de settings (seleccionar opción → ingresar valor → confirmar)

### Configuración de FSM

FSM ya está configurado en Runegram usando **RedisStorage2** (ver `run.py`):

```python
storage = RedisStorage2(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    pool_size=10,
    prefix='fsm'
)

dp = Dispatcher(bot, storage=storage)
```

### Definir Estados

```python
from aiogram.dispatcher.filters.state import State, StatesGroup

class CharacterCreationStates(StatesGroup):
    """Estados del flujo de creación de personaje con FSM."""
    waiting_for_name = State()
```

### Iniciar FSM desde un Callback

```python
async def handle_character_creation(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """Inicia el flujo de creación de personaje usando FSM."""

    # Verificar que no tenga personaje ya
    account = await player_service.get_or_create_account(session, callback.from_user.id)
    if account.character:
        await callback.answer("Ya tienes un personaje creado.", show_alert=True)
        return

    # Iniciar FSM
    state = dp.current_state(user=callback.from_user.id)
    await state.set_state(CharacterCreationStates.waiting_for_name)

    # Editar mensaje para solicitar nombre
    await callback.message.edit_text(
        "✨ <b>Creación de Personaje</b>\n\n"
        "Por favor, escribe el nombre que deseas para tu personaje.\n\n"
        "<i>Ejemplo: Aragorn</i>\n\n"
        "El nombre debe tener entre 3 y 20 caracteres y solo puede contener letras.",
        parse_mode="HTML"
    )
    await callback.answer()
```

## Crear Nuevos Tipos de Botones

### Paso 1: Crear Función en `inline_keyboards.py`

```python
def create_shop_item_keyboard(items: List[Item], page: int = 1) -> InlineKeyboardMarkup:
    """Crea un teclado inline para comprar items de una tienda."""
    keyboard = InlineKeyboardMarkup(row_width=1)

    for item in items:
        button = InlineKeyboardButton(
            text=f"{item.get_name()} - 💰{item.price}",
            callback_data=create_callback_data("buy_item", item_id=item.id)
        )
        keyboard.add(button)

    return keyboard
```

### Paso 2: Crear Handler en `callbacks.py`

```python
async def handle_buy_item(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """Maneja la compra de un item desde la tienda."""
    item_id = params.get("item_id")
    if not item_id:
        await callback.answer("Error: Item no especificado.", show_alert=True)
        return

    # Lógica de compra...
```

### Paso 3: Registrar Handler en `CALLBACK_HANDLERS`

```python
CALLBACK_HANDLERS = {
    "create_char": handle_character_creation,
    "move": handle_movement,
    "refresh": handle_refresh,
    "buy_item": handle_buy_item,  # ← NUEVO
}
```

## Mejores Prácticas

### 1. Validación de Parámetros

```python
async def handle_action(callback, params, session):
    required_id = params.get("required_id")
    if not required_id:
        await callback.answer("Error: Parámetro faltante.", show_alert=True)
        return
```

### 2. Manejo de Errores

```python
async def handle_action(callback, params, session):
    try:
        # Lógica del handler
        pass
    except Exception:
        logging.exception("Error en handler")
        await callback.answer("❌ Ocurrió un error inesperado.", show_alert=True)
```

### 3. Feedback Visual

**Siempre llama `callback.answer()`** incluso si no muestras mensaje:

```python
# ✅ Bueno - Telegram no muestra "loading" infinito
await callback.answer()

# ❌ Malo - Telegram muestra loading por 30 segundos
# (no llamar callback.answer())
```

### 4. Callback Data Conciso

```python
# ✅ Bueno - 17 bytes
create_callback_data("mv", dir="n", r=123)

# ❌ Malo - 45 bytes (innecesariamente largo)
create_callback_data("move_character", direction="north", room_id=123)
```

## Ver También

- [Command System](sistema-de-comandos.md) - Sistema de comandos
- [Output Style Guide](../creacion-de-contenido/guia-de-estilo-de-salida.md) - Guía de estilo
