---
título: "Sistema de Desambiguación de Objetos (Ordinales)"
categoría: "Sistemas del Motor"
versión: "1.0"
última_actualización: "2025-10-09"
autor: "Proyecto Runegram"
etiquetas: ["ordinales", "desambiguación", "objetos", "estándar-mud"]
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-comandos.md"
  - "creacion-de-contenido/guia-de-estilo-de-salida.md"
referencias_código:
  - "commands/player/interaction.py"
  - "src/templates/base/inventory.html.j2"
  - "src/templates/base/room.html.j2"
estado: "actual"
---

# Item Disambiguation System (Ordinales)

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

## 6. Diseño y Consideraciones

### ¿Por Qué Ordinales y No IDs?

**Alternativa rechazada: IDs únicos** (`/coger #12345`)
- ❌ No intuitivo para jugadores nuevos
- ❌ Requiere mostrar IDs constantemente (ruido visual)
- ❌ No es el estándar MUD

**Solución elegida: Ordinales** (`/coger 2.espada`)
- ✅ Estándar de la industria MUD (Diku, CircleMUD, ROM)
- ✅ Intuitivo: corresponde a números en pantalla
- ✅ Retrocompatible: funciona sin números si no hay duplicados
- ✅ Flexible: números cambian dinámicamente con inventario

### Retrocompatibilidad

El sistema es **100% retrocompatible**:
- Si solo hay un objeto, no se necesitan ordinales
- Los comandos antiguos (`/coger espada`) siguen funcionando
- Solo se requieren ordinales cuando hay ambigüedad real

### UX para Telegram Móvil

**Desafío:** Pantallas pequeñas, teclado táctil.

**Soluciones:**
1. **Mensajes de desambiguación claros** con ejemplos de uso
2. **Sintaxis simple:** solo `N.nombre`, no sintaxis compleja
3. **Formato HTML:** resalta sintaxis con `<code>` tags
4. **Números visibles:** siempre se muestran en listados

## 7. Mejores Prácticas para Desarrolladores

### Al Crear Nuevos Comandos

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

### Manejo de Errores

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

### Parse Mode Obligatorio

Los mensajes de desambiguación usan HTML para formato:

```python
# ❌ MAL - Perderá formato
await message.answer(error_msg)

# ✅ BIEN - Preserva formato
await message.answer(error_msg, parse_mode="HTML")
```

## Ver También

- [Command System](sistema-de-comandos.md) - Sistema de comandos
- [Output Style Guide](../creacion-de-contenido/guia-de-estilo-de-salida.md) - Guía de estilo de outputs
- [Command Reference](../referencia/referencia-de-comandos.md) - Referencia de comandos
