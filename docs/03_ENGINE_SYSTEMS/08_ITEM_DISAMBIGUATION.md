# Sistema de Desambiguación de Items (Ordinales)

El Sistema de Desambiguación resuelve uno de los problemas más comunes en MUDs: **cómo identificar objetos específicos cuando hay múltiples instancias con el mismo nombre**. Runegram implementa el patrón estándar de ordinales usado en MUDs clásicos (Diku, CircleMUD), proporcionando una solución elegante, intuitiva y retrocompatible.

## 1. El Problema

Cuando un jugador tiene dos espadas en su inventario y ejecuta `/coger espada`, ¿cuál debería tomar el sistema? El enfoque ingenuo sería tomar siempre la primera, pero esto es frustrante e impide la interacción granular con el mundo.

**Ejemplo del problema:**
```
📦 Tu Inventario:
⚔️ espada oxidada
⚔️ espada brillante
🎒 mochila de cuero

/dejar espada  → ¿Cuál espada? Siempre la primera es frustrante.
```

## 2. La Solución: Sistema de Ordinales

Runegram implementa dos mecanismos complementarios:

### 2.1 Numeración Visual Automática

Todos los listados de items (inventario, sala, contenedores) muestran números automáticamente:

```
📦 Tu Inventario:
1. ⚔️ espada oxidada
2. 🎒 mochila de cuero
3. ⚔️ espada brillante
4. 🧪 poción de vida
```

**Implementación:** Templates Jinja2 usan `{{ loop.index }}` en lugar de guiones.

**Archivos afectados:**
- `src/templates/base/inventory.html.j2`
- `src/templates/base/room.html.j2`
- `src/templates/base/item_look.html.j2`

### 2.2 Sintaxis de Ordinales: `N.nombre`

Los jugadores pueden usar la sintaxis `N.nombre` para especificar exactamente qué objeto quieren:

```
/coger 1.espada    → Coge la primera espada (oxidada)
/coger 3.espada    → Coge la tercera espada (brillante)
/meter 2.pocion en 1.mochila  → Mete la 2da poción en la 1ra mochila
```

**Características:**
- **Basado en 1:** Los números empiezan en 1 (más intuitivo para jugadores)
- **Retrocompatible:** Si solo hay un objeto, no se necesitan ordinales
- **Flexible:** Funciona en cualquier comando que busque items

## 3. Arquitectura de Implementación

### 3.1 Función Central: `find_item_in_list_with_ordinal()`

**Ubicación:** `commands/player/interaction.py`

```python
def find_item_in_list_with_ordinal(
    search_term: str,
    item_list: list,
    enable_disambiguation: bool = True
) -> tuple:
    """
    Busca un item con soporte para ordinales y desambiguación.

    Args:
        search_term: Término de búsqueda (puede incluir ordinal "N.nombre")
        item_list: Lista de objetos Item donde buscar
        enable_disambiguation: Si True, genera mensajes de desambiguación

    Returns:
        tuple: (item_encontrado | None, mensaje_error | None)
    """
```

### 3.2 Algoritmo de Búsqueda

**Paso 1: Detección de Ordinal**
```python
ordinal_match = re.match(r'^(\d+)\.(.+)', search_term)
```

Si hay ordinal (ej: "2.espada"):
1. Extrae el número: `2`
2. Extrae el nombre: `"espada"`
3. Busca todos los items con ese nombre
4. Valida que el ordinal esté en rango válido
5. Retorna el item en la posición ordinal (1-indexed)

**Paso 2: Búsqueda Sin Ordinal**

Si NO hay ordinal (ej: "espada"):
1. Busca todos los items que coincidan
2. Si hay 0 matches → retorna `(None, None)`
3. Si hay 1 match → retorna `(item, None)`
4. Si hay N matches → retorna `(None, mensaje_desambiguación)`

### 3.3 Mensajes de Desambiguación

Cuando hay múltiples coincidencias sin ordinal, el sistema genera un mensaje interactivo:

```
❓ Hay 2 'espada'. ¿Cuál quieres coger?

1. ⚔️ espada oxidada
2. ⚔️ espada brillante

Usa:
/coger 1.espada
/coger 2.espada
```

**Formato HTML:** Los mensajes usan `<code>` para resaltar la sintaxis correcta.

## 4. Integración en Comandos

### 4.1 Patrón Estándar (Un Solo Objeto)

Para comandos que buscan un solo objeto (`/coger`, `/dejar`, `/mirar`):

```python
# Buscar con soporte para ordinales
item_to_get, error_msg = find_item_in_list_with_ordinal(
    item_name,
    character.room.items,
    enable_disambiguation=True
)

# Manejar desambiguación
if error_msg:
    await message.answer(error_msg, parse_mode="HTML")
    return

if not item_to_get:
    await message.answer("No ves ese objeto por aquí.")
    return

# Continuar con lógica del comando...
```

### 4.2 Patrón Doble Objeto (Contenedores)

Para comandos que buscan DOS objetos (`/meter`, `/sacar`):

```python
# 1. Buscar contenedor con ordinales
available_containers = character.items + character.room.items
container, container_error = find_item_in_list_with_ordinal(
    container_name,
    available_containers,
    enable_disambiguation=True
)

if container_error:
    await message.answer(container_error, parse_mode="HTML")
    return

# 2. Validar contenedor...

# 3. Buscar item con ordinales
available_items = character.items + character.room.items
item_to_store, item_error = find_item_in_list_with_ordinal(
    item_name,
    available_items,
    enable_disambiguation=True
)

if item_error:
    await message.answer(item_error, parse_mode="HTML")
    return

# 4. Ejecutar acción...
```

**Clave:** Ambos argumentos soportan ordinales independientemente.

## 5. Comandos Implementados

✅ **Comandos con Soporte de Ordinales:**

| Comando | Soporte | Ejemplo |
|---------|---------|---------|
| `/mirar` | ✅ Objetos | `/mirar 2.espada` |
| `/coger` | ✅ Objetos | `/coger 3.pocion` |
| `/dejar` | ✅ Objetos | `/dejar 1.espada` |
| `/meter` | ✅ Item + Contenedor | `/meter 2.pocion en 1.mochila` |
| `/sacar` | ✅ Item + Contenedor | `/sacar 1.daga de 2.cofre` |
| `/inventario` | ✅ Contenedores | `/inv 2.mochila` |

## 6. Casos de Uso y Ejemplos

### Caso 1: Dos Espadas Idénticas

**Situación:** Jugador tiene dos espadas con el mismo nombre.

```
📦 Tu Inventario:
1. ⚔️ espada oxidada
2. 🎒 mochila
3. ⚔️ espada brillante
```

**Comandos:**
```
/dejar espada           → Desambiguación (hay 2)
/dejar 1.espada         → Deja la espada oxidada
/dejar 3.espada         → Deja la espada brillante
/mirar 1.espada         → Examina la espada oxidada
```

### Caso 2: Múltiples Contenedores

**Situación:** Jugador tiene 3 mochilas.

```
📦 Tu Inventario:
1. 🎒 mochila de cuero (vacía)
2. ⚔️ espada
3. 🎒 mochila de tela (2 items)
4. 🎒 mochila grande (5 items)
```

**Comandos:**
```
/meter espada en mochila       → Desambiguación (hay 3 mochilas)
/meter espada en 1.mochila     → Guarda en la 1ra mochila (cuero)
/meter espada en 4.mochila     → Guarda en la 3ra mochila (grande)
/inv 3.mochila                 → Ver contenido de mochila de tela
```

### Caso 3: Item y Contenedor Duplicados

**Situación:** 2 pociones + 2 mochilas.

```
📦 Tu Inventario:
1. 🧪 poción de vida
2. 🎒 mochila pequeña
3. 🧪 poción de vida
4. 🎒 mochila grande
```

**Comandos:**
```
/meter pocion en mochila           → Doble desambiguación
/meter 1.pocion en 2.mochila       → Preciso
/meter 3.pocion en 4.mochila       → Preciso
/sacar 1.pocion de 2.mochila       → Preciso al sacar
```

## 7. Validaciones y Errores

### 7.1 Validación de Rango

```python
if ordinal_num < 1:
    return None, f"El número debe ser 1 o mayor."

if ordinal_num > len(matches):
    if len(matches) == 1:
        return None, f"Solo hay 1 '{item_name}'."
    else:
        return None, f"Solo hay {len(matches)} '{item_name}'."
```

### 7.2 Mensajes de Error Informativos

**Ordinal fuera de rango:**
```
> /coger 5.espada
Solo hay 2 'espada'.
```

**Ordinal cero o negativo:**
```
> /coger 0.espada
El número debe ser 1 o mayor.
```

**Objeto no encontrado:**
```
> /coger 2.hacha
No ves ese objeto por aquí.
```

## 8. Consideraciones de Diseño

### 8.1 ¿Por Qué Ordinales y No IDs?

**Alternativa rechazada: IDs únicos** (`/coger #12345`)
- ❌ No intuitivo para jugadores nuevos
- ❌ Requiere mostrar IDs constantemente (ruido visual)
- ❌ No es el estándar MUD

**Solución elegida: Ordinales** (`/coger 2.espada`)
- ✅ Estándar de la industria MUD (Diku, CircleMUD, ROM)
- ✅ Intuitivo: corresponde a números en pantalla
- ✅ Retrocompatible: funciona sin números si no hay duplicados
- ✅ Flexible: números cambian dinámicamente con inventario

### 8.2 Retrocompatibilidad

El sistema es **100% retrocompatible**:
- Si solo hay un objeto, no se necesitan ordinales
- Los comandos antiguos (`/coger espada`) siguen funcionando
- Solo se requieren ordinales cuando hay ambigüedad real

### 8.3 UX para Telegram Móvil

**Desafío:** Pantallas pequeñas, teclado táctil.

**Soluciones:**
1. **Mensajes de desambiguación claros** con ejemplos de uso
2. **Sintaxis simple:** solo `N.nombre`, no sintaxis compleja
3. **Formato HTML:** resalta sintaxis con `<code>` tags
4. **Números visibles:** siempre se muestran en listados

## 9. Extensibilidad Futura

### 9.1 Posibles Mejoras

**Botones Inline para Desambiguación:**
```
❓ Hay 2 'espada'. ¿Cuál quieres coger?

[1. espada oxidada]  [2. espada brillante]
```

Implementación:
- Generar inline keyboard en `find_item_in_list_with_ordinal()`
- Callback data: `disambiguate:coger:item_id:5`
- Ejecutar comando original con item seleccionado

**Aliases de Ordinales:**
- `first.espada`, `last.espada`
- `all.pocion` para acciones masivas

### 9.2 Aplicación a Otros Sistemas

El patrón de ordinales puede extenderse a:
- **NPCs:** `/atacar 2.goblin` cuando hay múltiples goblins
- **Salidas:** `/usar 2.norte` si hay múltiples salidas al norte (raro)
- **Comandos Dinámicos:** Cualquier búsqueda en listas

## 10. Mejores Prácticas para Desarrolladores

### 10.1 Al Crear Nuevos Comandos

**SIEMPRE** usa `find_item_in_list_with_ordinal()` en lugar de `find_item_in_list()`:

```python
# ❌ MAL - Sin soporte de ordinales
item = find_item_in_list(item_name, character.items)

# ✅ BIEN - Con soporte de ordinales
item, error_msg = find_item_in_list_with_ordinal(
    item_name,
    character.items,
    enable_disambiguation=True
)

if error_msg:
    await message.answer(error_msg, parse_mode="HTML")
    return
```

### 10.2 Manejo de Errores

**SIEMPRE** maneja ambos retornos (item y error_msg):

```python
item, error_msg = find_item_in_list_with_ordinal(...)

# 1. Error/desambiguación tiene prioridad
if error_msg:
    await message.answer(error_msg, parse_mode="HTML")
    return

# 2. Luego verificar si se encontró algo
if not item:
    await message.answer("No tienes ese objeto.")
    return

# 3. Continuar con lógica del comando
```

### 10.3 Parse Mode Obligatorio

Los mensajes de desambiguación usan HTML para formato:

```python
# ❌ MAL - Perderá formato
await message.answer(error_msg)

# ✅ BIEN - Preserva formato
await message.answer(error_msg, parse_mode="HTML")
```

### 10.4 Documentación en Comandos

Menciona el soporte de ordinales en docstrings:

```python
class CmdGet(Command):
    """
    Comando para recoger objetos.

    Soporta ordinales para objetos duplicados:
    - /coger espada      → Coge espada (si solo hay una)
    - /coger 2.espada    → Coge la segunda espada
    """
```

## 11. Testing y Debugging

### 11.1 Casos de Test Recomendados

**Test 1: Un Solo Item**
- Crear 1 espada
- `/coger espada` → Debe funcionar sin ordinales

**Test 2: Items Duplicados Sin Ordinal**
- Crear 2 espadas
- `/coger espada` → Debe mostrar desambiguación

**Test 3: Ordinales Válidos**
- Crear 3 espadas
- `/coger 1.espada` → Primera espada
- `/coger 3.espada` → Tercera espada

**Test 4: Ordinales Inválidos**
- Crear 2 espadas
- `/coger 0.espada` → Error (mínimo 1)
- `/coger 5.espada` → Error (solo hay 2)

**Test 5: Doble Ordinal (Contenedores)**
- Crear 2 pociones + 2 mochilas
- `/meter 1.pocion en 2.mochila` → Debe funcionar
- `/meter pocion en mochila` → Doble desambiguación

### 11.2 Logging de Debugging

Para debugging, agregar logs en `find_item_in_list_with_ordinal()`:

```python
logging.debug(f"Búsqueda: '{search_term}' en {len(item_list)} items")
if ordinal_match:
    logging.debug(f"Ordinal detectado: {ordinal_num}.{item_name}")
logging.debug(f"Matches encontrados: {len(matches)}")
```

## 12. Referencias

### 12.1 Código Fuente

- **Función principal:** `commands/player/interaction.py:find_item_in_list_with_ordinal()`
- **Comandos actualizados:**
  - `commands/player/interaction.py` (CmdGet, CmdDrop, CmdPut, CmdTake)
  - `commands/player/general.py` (CmdLook, CmdInventory)
- **Templates:** `src/templates/base/*.html.j2`

### 12.2 Documentación Relacionada

- **Referencia de comandos:** `docs/COMMAND_REFERENCE.md` (sección "Sistema de Ordinales")
- **Guía de desarrollo:** `CLAUDE.md` (Sistema 11)
- **Sistema de comandos:** `docs/03_ENGINE_SYSTEMS/01_COMMAND_SYSTEM.md`

### 12.3 Inspiración MUD

- **Diku MUD:** Sistema de ordinales `N.nombre` original
- **CircleMUD:** Refinamiento del sistema Diku
- **ROM:** Extensión con soporte de keywords múltiples

---

**Versión:** 1.0
**Última actualización:** 2025-10-04
**Autor:** Sistema Runegram
**Estado:** ✅ Implementado y funcional
