# Sistema de Botones Inline de Telegram

**Versión**: 1.0
**Última actualización**: 2025-10-04

---

## 📋 Índice

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Formato de Callback Data](#formato-de-callback-data)
4. [Uso de FSM (Finite State Machine)](#uso-de-fsm-finite-state-machine)
5. [Crear Nuevos Tipos de Botones](#crear-nuevos-tipos-de-botones)
6. [Handlers de Callbacks](#handlers-de-callbacks)
7. [Ejemplos Completos](#ejemplos-completos)
8. [Mejores Prácticas](#mejores-prácticas)
9. [Roadmap Futuro](#roadmap-futuro)

---

## Introducción

El sistema de **botones inline** de Runegram permite a los jugadores interactuar con el juego mediante botones en lugar de comandos de texto. Esto mejora significativamente la experiencia de usuario en dispositivos móviles, reduciendo la necesidad de escribir comandos largos.

### Características Implementadas

- ✅ **Botón de creación de personaje** con flujo FSM
- ✅ **Botones de navegación** en salas (Norte, Sur, Este, Oeste, etc.)
- ✅ **Sistema de callback routing** extensible y escalable
- ✅ **Soporte para FSM** (multi-step conversations)
- ✅ **Callback data estructurado** y parseable

### Filosofía de Diseño

Este sistema fue diseñado pensando en:

- **Escalabilidad**: Fácil agregar nuevos tipos de botones
- **Mantenibilidad**: Código limpio y bien organizado
- **Robustez**: Manejo de errores y validaciones
- **Futuro**: Preparado para teclado dinámico completo (próximamente)

---

## Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                     Jugador en Telegram                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Presiona botón inline
                        ↓
┌─────────────────────────────────────────────────────────────┐
│            src/handlers/callbacks.py                        │
│                                                             │
│  callback_query_router()                                    │
│    ├─→ parse_callback_data()  (parsea acción y params)     │
│    └─→ CALLBACK_HANDLERS[action]  (ejecuta handler)        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Busca handler específico
                        ↓
┌─────────────────────────────────────────────────────────────┐
│              Handlers Específicos                           │
│                                                             │
│  • handle_character_creation()  → Inicia FSM               │
│  • handle_movement()           → Mueve personaje           │
│  • handle_refresh()            → Actualiza información     │
│  • [futuros handlers...]                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Utiliza helpers
                        ↓
┌─────────────────────────────────────────────────────────────┐
│         src/utils/inline_keyboards.py                       │
│                                                             │
│  • create_callback_data()           (genera callback_data)  │
│  • parse_callback_data()            (parsea callback_data)  │
│  • create_character_creation_keyboard()                     │
│  • create_room_navigation_keyboard()                        │
│  • create_confirmation_keyboard()                           │
│  • create_refresh_button()                                  │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Ejecución

1. **Jugador presiona botón** → Telegram envía `CallbackQuery`
2. **callback_query_router()** intercepta el callback
3. **parse_callback_data()** extrae acción y parámetros
4. **CALLBACK_HANDLERS** busca el handler correspondiente
5. **Handler específico** ejecuta la lógica (mover, crear personaje, etc.)
6. **Respuesta al jugador** vía `callback.answer()` o editando mensaje

---

## Formato de Callback Data

### Estructura

Todos los callbacks usan un formato estructurado y extensible:

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

# Confirmación (futuro)
"confirm_delete_char:char_id=5:confirm=yes"

# Uso de item (futuro)
"use_item:item_id=123"
```

### Funciones de Callback Data

#### `create_callback_data(action, **params)`

Crea una cadena de callback_data estructurada.

```python
from src.utils.inline_keyboards import create_callback_data

# Ejemplo 1: Movimiento
callback_data = create_callback_data("move", direction="norte")
# Resultado: "move:direction=norte"

# Ejemplo 2: Uso de item
callback_data = create_callback_data("use_item", item_id=5, action_type="consume")
# Resultado: "use_item:item_id=5:action_type=consume"
```

#### `parse_callback_data(callback_data)`

Parsea un string de callback_data en un diccionario.

```python
from src.utils.inline_keyboards import parse_callback_data

callback_info = parse_callback_data("move:direction=norte")
# Resultado: {'action': 'move', 'params': {'direction': 'norte'}}

callback_info = parse_callback_data("use_item:item_id=5:action_type=consume")
# Resultado: {'action': 'use_item', 'params': {'item_id': 5, 'action_type': 'consume'}}
```

**Nota**: La función automáticamente convierte valores numéricos a `int`.

---

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

Los estados se definen usando `StatesGroup`:

```python
from aiogram.dispatcher.filters.state import State, StatesGroup

class CharacterCreationStates(StatesGroup):
    """Estados del flujo de creación de personaje con FSM."""
    waiting_for_name = State()
    # Futuros estados podrían ser:
    # selecting_race = State()
    # selecting_class = State()
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

### Handler de Estado FSM

```python
@dp.message_handler(state=CharacterCreationStates.waiting_for_name)
async def process_character_name(message: types.Message, state: FSMContext):
    """Procesa el nombre del personaje cuando el usuario responde."""
    async with async_session_factory() as session:
        try:
            name = message.text.strip()

            # Validaciones
            if len(name) < 3:
                await message.answer("❌ El nombre debe tener al menos 3 caracteres.")
                return  # No finish() - sigue en el mismo estado

            if len(name) > 20:
                await message.answer("❌ El nombre es demasiado largo (máximo 20 caracteres).")
                return

            if not name.isalpha():
                await message.answer("❌ El nombre solo puede contener letras.")
                return

            # Verificar unicidad del nombre
            existing = await session.execute(
                select(Character).where(Character.name.ilike(name))
            )
            if existing.scalar_one_or_none():
                await message.answer(f"❌ El nombre '{name}' ya está en uso.")
                return

            # Crear personaje
            account = await player_service.get_or_create_account(session, message.from_user.id)
            character = await player_service.create_character(session, account, name)

            # Finalizar FSM
            await state.finish()

            # Mensaje de éxito
            await message.answer(
                f"✨ <b>¡Bienvenido, {character.name}!</b>\n\n"
                "Tu personaje ha sido creado exitosamente.",
                parse_mode="HTML"
            )

            # Mostrar sala inicial
            await show_current_room(message)

        except Exception:
            logging.exception("Error en creación de personaje")
            await message.answer("❌ Ocurrió un error al crear tu personaje.")
            await state.finish()
```

### Métodos de FSM

```python
# Obtener estado actual
state = dp.current_state(user=user_id, chat=chat_id)

# Establecer estado
await state.set_state(MyStatesGroup.waiting_for_input)

# Guardar datos en el contexto del estado
await state.update_data(key="value")

# Obtener datos del contexto
data = await state.get_data()

# Finalizar FSM (limpiar estado)
await state.finish()
```

---

## Crear Nuevos Tipos de Botones

### Paso 1: Crear Función en `inline_keyboards.py`

```python
# src/utils/inline_keyboards.py

def create_shop_item_keyboard(items: List[Item], page: int = 1) -> InlineKeyboardMarkup:
    """
    Crea un teclado inline para comprar items de una tienda.

    Args:
        items: Lista de items disponibles
        page: Página actual

    Returns:
        InlineKeyboardMarkup: Teclado con botones de items
    """
    keyboard = InlineKeyboardMarkup(row_width=1)

    for item in items:
        button = InlineKeyboardButton(
            text=f"{item.get_name()} - 💰{item.price}",
            callback_data=create_callback_data("buy_item", item_id=item.id)
        )
        keyboard.add(button)

    # Botones de navegación
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Anterior",
            callback_data=create_callback_data("shop_page", page=page-1)
        ))

    nav_buttons.append(InlineKeyboardButton(
        text="❌ Cerrar",
        callback_data=create_callback_data("close_shop")
    ))

    if len(items) > 10:  # Si hay más items
        nav_buttons.append(InlineKeyboardButton(
            text="➡️ Siguiente",
            callback_data=create_callback_data("shop_page", page=page+1)
        ))

    keyboard.row(*nav_buttons)

    return keyboard
```

### Paso 2: Crear Handler en `callbacks.py`

```python
# src/handlers/callbacks.py

async def handle_buy_item(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """
    Maneja la compra de un item desde la tienda.

    Args:
        callback: Callback query de Telegram
        params: Parámetros del callback_data (debe incluir 'item_id')
        session: Sesión de base de datos
    """
    item_id = params.get("item_id")
    if not item_id:
        await callback.answer("Error: Item no especificado.", show_alert=True)
        return

    # Obtener personaje
    account = await player_service.get_or_create_account(session, callback.from_user.id)
    if not account.character:
        await callback.answer("Primero debes crear un personaje.", show_alert=True)
        return

    character = account.character

    # Obtener item de la tienda
    item = await session.get(Item, item_id)
    if not item:
        await callback.answer("Este item ya no está disponible.", show_alert=True)
        return

    # Verificar que el jugador tenga dinero suficiente (lógica de ejemplo)
    if character.gold < item.price:
        await callback.answer(
            f"No tienes suficiente oro. Necesitas {item.price} 💰",
            show_alert=True
        )
        return

    # Realizar compra
    character.gold -= item.price

    # Crear instancia del item en inventario
    new_item = Item(
        key=item.key,
        character_id=character.id
    )
    session.add(new_item)
    await session.commit()

    # Respuesta
    await callback.answer(f"¡Compraste {item.get_name()}! 💰 -{item.price}")
    await callback.message.edit_text(
        f"✅ <b>Compra Exitosa</b>\n\n"
        f"Has comprado {item.get_name()}.\n"
        f"Oro restante: {character.gold} 💰",
        parse_mode="HTML"
    )
```

### Paso 3: Registrar Handler en `CALLBACK_HANDLERS`

```python
# src/handlers/callbacks.py

CALLBACK_HANDLERS = {
    "create_char": handle_character_creation,
    "move": handle_movement,
    "refresh": handle_refresh,
    "buy_item": handle_buy_item,          # ← NUEVO
    "shop_page": handle_shop_page,        # ← NUEVO
    "close_shop": handle_close_shop,      # ← NUEVO
}
```

### Paso 4: Usar en Comando

```python
# commands/player/interaction.py

class CmdShop(Command):
    """Comando para abrir la tienda."""
    names = ["tienda", "shop"]
    description = "Abre la tienda de items."

    async def execute(self, character, session, message, args):
        # Obtener items de la tienda
        shop_items = await get_shop_items(session)

        # Crear teclado
        from src.utils.inline_keyboards import create_shop_item_keyboard
        keyboard = create_shop_item_keyboard(shop_items, page=1)

        # Enviar mensaje con botones
        await message.answer(
            "🏪 <b>Tienda de Runegram</b>\n\n"
            "Selecciona un item para comprar:",
            parse_mode="HTML",
            reply_markup=keyboard
        )
```

---

## Handlers de Callbacks

### Estructura de un Handler

```python
async def handle_action_name(
    callback: types.CallbackQuery,
    params: dict,
    session: AsyncSession
):
    """
    Descripción de la acción.

    Args:
        callback: Callback query de Telegram
        params: Parámetros parseados del callback_data
        session: Sesión de base de datos
    """
    try:
        # 1. Validar parámetros
        required_param = params.get("required_param")
        if not required_param:
            await callback.answer("Error: Parámetro faltante.", show_alert=True)
            return

        # 2. Obtener contexto del jugador
        account = await player_service.get_or_create_account(
            session,
            callback.from_user.id
        )

        # 3. Validaciones de lógica de negocio
        if not some_condition:
            await callback.answer("No puedes hacer eso ahora.", show_alert=True)
            return

        # 4. Ejecutar acción
        result = await perform_action(session, account, params)

        # 5. Actualizar BD si es necesario
        await session.commit()

        # 6. Feedback al usuario
        await callback.answer("✅ Acción completada.")

        # 7. Actualizar mensaje (opcional)
        await callback.message.edit_text(
            "Nuevo contenido del mensaje",
            parse_mode="HTML"
        )

    except Exception:
        logging.exception(f"Error en handler de acción para usuario {callback.from_user.id}")
        await callback.answer("❌ Ocurrió un error.", show_alert=True)
```

### Métodos de CallbackQuery

```python
# Feedback visual (popup pequeño)
await callback.answer("Mensaje corto")

# Alerta (popup grande que requiere OK)
await callback.answer("Mensaje importante", show_alert=True)

# Editar mensaje del botón
await callback.message.edit_text("Nuevo texto")

# Editar mensaje con nuevo teclado
await callback.message.edit_text(
    "Nuevo texto",
    reply_markup=new_keyboard
)

# Eliminar mensaje
await callback.message.delete()

# Enviar nuevo mensaje
await callback.message.answer("Mensaje adicional")
```

---

## Ejemplos Completos

### Ejemplo 1: Botones de Confirmación

**Caso de Uso**: Confirmar antes de dejar un item valioso.

```python
# src/utils/inline_keyboards.py

def create_drop_confirmation_keyboard(item_id: int) -> InlineKeyboardMarkup:
    """Crea botones de confirmación para dejar un item."""
    keyboard = InlineKeyboardMarkup(row_width=2)

    yes_button = InlineKeyboardButton(
        text="✅ Sí, dejar",
        callback_data=create_callback_data("confirm_drop", item_id=item_id, confirm="yes")
    )
    no_button = InlineKeyboardButton(
        text="❌ Cancelar",
        callback_data=create_callback_data("confirm_drop", item_id=item_id, confirm="no")
    )

    keyboard.row(yes_button, no_button)
    return keyboard
```

```python
# commands/player/interaction.py

class CmdDrop(Command):
    """Comando mejorado con confirmación para items valiosos."""

    async def execute(self, character, session, message, args):
        # ... búsqueda del item ...

        # Si el item es valioso, pedir confirmación
        if item.prototype.get("is_valuable"):
            keyboard = create_drop_confirmation_keyboard(item.id)
            await message.answer(
                f"⚠️ ¿Estás seguro de dejar <b>{item.get_name()}</b>?\n"
                f"Este es un objeto valioso.",
                parse_mode="HTML",
                reply_markup=keyboard
            )
            return

        # Si no es valioso, dejar directamente
        # ...
```

```python
# src/handlers/callbacks.py

async def handle_confirm_drop(callback, params, session):
    """Maneja confirmación de dejar item."""
    item_id = params.get("item_id")
    confirm = params.get("confirm")

    if confirm == "no":
        await callback.answer("Cancelado.")
        await callback.message.delete()
        return

    # Confirmar = dejar el item
    account = await player_service.get_or_create_account(session, callback.from_user.id)
    character = account.character

    item = await session.get(Item, item_id)

    # Mover item al suelo
    item.character_id = None
    item.room_id = character.room_id
    await session.commit()

    await callback.answer(f"Dejaste {item.get_name()}.")
    await callback.message.edit_text(f"Has dejado <b>{item.get_name()}</b>.", parse_mode="HTML")

    # Notificar a otros en la sala
    await broadcaster_service.send_message_to_room(
        session=session,
        room=character.room,
        message_text=f"<i>{character.name} deja {item.get_name()}.</i>",
        exclude_character_id=character.id
    )

# Registrar en CALLBACK_HANDLERS
CALLBACK_HANDLERS = {
    # ...
    "confirm_drop": handle_confirm_drop,
}
```

### Ejemplo 2: Paginación con Botones

**Caso de Uso**: Inventario con múltiples páginas.

```python
# src/utils/inline_keyboards.py

def create_inventory_page_keyboard(
    items: List[Item],
    page: int,
    total_pages: int,
    per_page: int = 5
) -> InlineKeyboardMarkup:
    """Crea teclado de inventario con paginación."""
    keyboard = InlineKeyboardMarkup(row_width=1)

    # Calcular slice de items para esta página
    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]

    # Botones de items
    for item in page_items:
        button = InlineKeyboardButton(
            text=f"{item.get_name()}",
            callback_data=create_callback_data("view_item", item_id=item.id)
        )
        keyboard.add(button)

    # Botones de navegación
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=create_callback_data("inv_page", page=page-1)
        ))

    nav_buttons.append(InlineKeyboardButton(
        text=f"📄 {page}/{total_pages}",
        callback_data="noop"  # No hace nada
    ))

    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(
            text="➡️",
            callback_data=create_callback_data("inv_page", page=page+1)
        ))

    keyboard.row(*nav_buttons)

    return keyboard
```

---

## Mejores Prácticas

### 1. Validación de Parámetros

**Siempre valida** que los parámetros esperados existan:

```python
async def handle_action(callback, params, session):
    required_id = params.get("required_id")
    if not required_id:
        await callback.answer("Error: Parámetro faltante.", show_alert=True)
        return

    # Continuar con lógica
```

### 2. Manejo de Errores

**Nunca dejes que una excepción llegue al usuario sin feedback**:

```python
async def handle_action(callback, params, session):
    try:
        # Lógica del handler
        pass
    except SpecificException as e:
        logging.error(f"Error específico: {e}")
        await callback.answer("Algo salió mal específicamente.", show_alert=True)
    except Exception:
        logging.exception("Error general en handler")
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

### 4. Editar vs. Enviar

**Edita mensajes existentes** cuando sea posible para evitar spam:

```python
# ✅ Bueno - Actualiza mensaje existente
await callback.message.edit_text("Nuevo contenido")

# ⚠️ Aceptable solo si necesitas múltiples mensajes
await callback.answer("Confirmación")
await callback.message.answer("Nuevo mensaje adicional")
```

### 5. Callback Data Conciso

**Usa nombres cortos** para parámetros (límite de 64 bytes):

```python
# ✅ Bueno - 17 bytes
create_callback_data("mv", dir="n", r=123)

# ❌ Malo - 45 bytes (innecesariamente largo)
create_callback_data("move_character", direction="north", room_id=123)
```

### 6. Seguridad

**Valida permisos** antes de ejecutar acciones:

```python
async def handle_admin_action(callback, params, session):
    account = await player_service.get_or_create_account(session, callback.from_user.id)

    # Verificar rol
    if account.role not in ["ADMIN", "SUPERADMIN"]:
        await callback.answer("⛔ No tienes permiso.", show_alert=True)
        return

    # Continuar con acción de admin
```

---

## Roadmap Futuro

### Fase 1: Botones Básicos (✅ COMPLETADO)

- ✅ Sistema de callback routing
- ✅ Botón de creación de personaje con FSM
- ✅ Botones de navegación en salas
- ✅ Helpers para crear botones comunes

### Fase 2: Teclado Dinámico Completo (🚧 PRÓXIMAMENTE)

**Objetivo**: Permitir jugar casi sin escribir comandos.

#### Teclado Contextual de Sala

```
┌──────────────────────────────────────┐
│ Plaza Central de Runegard           │
├──────────────────────────────────────┤
│ [ ⬆️ Norte ]  [ ⬇️ Sur ]            │
│ [ ➡️ Este  ]  [ ⬅️ Oeste ]          │
├──────────────────────────────────────┤
│ [ 🎒 Inventario ]  [ 👥 Jugadores ]  │
│ [ 💬 Hablar     ]  [ 🔄 Actualizar ] │
└──────────────────────────────────────┘
```

#### Teclado de Inventario

```
┌──────────────────────────────────────┐
│ Tu Inventario (5 items)              │
├──────────────────────────────────────┤
│ 1. ⚔️ Espada Herrumbrosa            │
│    [ 🔍 Ver ]  [ 🗑️ Dejar ]  [ ⚡ Usar ] │
│                                      │
│ 2. 🧪 Poción de Vida Menor           │
│    [ 🔍 Ver ]  [ 🗑️ Dejar ]  [ ⚡ Usar ] │
├──────────────────────────────────────┤
│ [ ⬅️ ]  [ 📄 1/2 ]  [ ➡️ ]          │
└──────────────────────────────────────┘
```

#### Teclado de Combate (Sistema de Combate Futuro)

```
┌──────────────────────────────────────┐
│ ⚔️ Combate: Tú vs Orco               │
│ ❤️ 85/100   |   ❤️ 60/80            │
├──────────────────────────────────────┤
│ [ ⚔️ Atacar ]  [ 🛡️ Defender ]       │
│ [ ⚡ Habilidad ]  [ 🧪 Item ]        │
│ [ 🏃 Huir ]                          │
└──────────────────────────────────────┘
```

### Fase 3: Configuración de Settings con Menús (⏳ FUTURO)

```
┌──────────────────────────────────────┐
│ ⚙️ Configuración de Runegram         │
├──────────────────────────────────────┤
│ [ 📢 Canales ]                       │
│ [ 🔔 Notificaciones ]                │
│ [ 🎨 Tema (Claro/Oscuro) ]           │
│ [ 🌐 Idioma ]                        │
└──────────────────────────────────────┘
```

### Fase 4: NPCs Interactivos (⏳ FUTURO)

```
┌──────────────────────────────────────┐
│ 🧙 Mago Aldeano                      │
│ "¡Saludos, aventurero!"              │
├──────────────────────────────────────┤
│ [ 💬 Hablar ]                        │
│ [ 🛒 Comerciar ]                     │
│ [ 📜 Quest: Buscar Gema Perdida ]    │
└──────────────────────────────────────┘
```

### Consideraciones Técnicas Futuras

#### Persistencia de Estado UI

Para mantener la experiencia fluida, necesitaremos guardar el estado de la UI en Redis:

```python
# Guardar último mensaje con botones
await redis_client.set(
    f"ui_state:{character_id}",
    json.dumps({
        "message_id": message.message_id,
        "context": "inventory",
        "page": 2
    }),
    ex=3600  # 1 hora
)
```

#### Actualización Reactiva

Los botones deberían actualizarse automáticamente cuando cambia el estado:

```python
# Ejemplo: Al coger un item, actualizar botón de sala
async def update_room_ui(character_id):
    """Actualiza el teclado de sala para un personaje."""
    ui_state = await get_ui_state(character_id)
    if ui_state and ui_state["context"] == "room":
        # Re-renderizar botones con nueva info
        new_keyboard = create_room_navigation_keyboard(room)
        await bot.edit_message_reply_markup(
            chat_id=ui_state["chat_id"],
            message_id=ui_state["message_id"],
            reply_markup=new_keyboard
        )
```

---

## Conclusión

El sistema de botones inline de Runegram está diseñado para ser **escalable**, **mantenible** y **extensible**. Aunque actualmente solo implementa funcionalidad básica (creación de personaje y navegación), la arquitectura está preparada para soportar un **teclado dinámico completo** que eventualmente permitirá jugar casi sin escribir comandos.

**Principios clave**:
- ✅ Callbacks estructurados y parseables
- ✅ Router centralizado y extensible
- ✅ FSM para flujos multi-paso
- ✅ Validación y manejo de errores robusto
- ✅ Preparado para futuro complejo

Para agregar nueva funcionalidad, sigue los pasos de la sección **"Crear Nuevos Tipos de Botones"** y mantén siempre la consistencia con el sistema existente.

---

**Última Revisión**: 2025-10-04
**Próxima Actualización Planificada**: Fase 2 - Teclado Dinámico Completo
