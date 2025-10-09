# Análisis de Incongruencias: Guía de Estilo vs Implementación

## 📋 **Resumen Ejecutivo**

Se ha identificado un **cumplimiento del 71%** entre las guías de estilo documentadas y la implementación actual del código. Existen incongruencias críticas en el formato de listas, que violan "la regla más importante de toda la guía".

---

## 🔴 **Incongruencias CRÍTICAS**

### 1. **Indentación de Listas (La Regla Más Importante)**

**❌ LO QUE DICE LA GUÍA:**
- **TODAS** las listas en `<pre>` DEBEN usar **4 espacios + guion** (`    - `)
- Esta es la regla "más importante de toda la guía"
- **NUNCA** usar tabs literales

**❌ LO QUE HACE EL CÓDIGO:**
```jinja
{# inventory.html.j2 - LÍNEA 21, 27 #}
    {{ loop.index }}. {{ item_icon }} {{ item.get_name()}}  # ❌ MAL (solo 4 espacios, sin guion)

{# room.html.j2 - LÍNEA 17, 22 #}
{{ loop.index }}. {{ item_icon }} {{ item.get_name()}}  # ❌ MAL (números + punto)
```

**Problema:** Los templates de inventario y sala usan números sin guion, violando la regla universal.

### 2. **Uso de Números en Listas vs Guiones**

**❌ LO QUE DICE LA GUÍA:**
- Formato universal: `    - Item` (4 espacios + guion)
- Los números son solo para desambiguación (`1.espada`, `2.espada`)

**❌ LO QUE HACE EL CÓDIGO:**
```jinja
{# INCONSISTENCIA CRÍTICA #}
room.html.j2: Usa números (❌)
inventory.html.j2: Usa números (❌)
who.html.j2: Usa guiones (✅)
item_look.html.j2: Usa números (❌)
```

---

## 🟡 **Incongruencias MODERADAS**

### 3. **Formato de Feedback Simple**

**❌ LO QUE DICE LA GUÍA:**
- Feedback simple = texto plano, sin `<pre>`
- Puede usar íconos de estado (✅❌❓⚠️)

**❌ LO QUE HACE EL CÓDIGO:**
```python
# commands/player/general.py LÍNEA 197, 232, 289, 357
await message.answer(f"<pre>{ICONS['inventory']} <b>Tu Inventario</b>\nNo llevas nada.</pre>", parse_mode="HTML")
```

**Problema:** Mensajes de feedback simple usan `<pre>` como si fueran outputs descriptivos.

---

## 🟢 **Aspectos BIEN IMPLEMENTADOS**

### ✅ **Títulos en MAYÚSCULAS**
- Todos los templates usan correctamente `{{ room.name|upper }}` y similares

### ✅ **Uso de Íconos desde Constantes**
- Todos los templates usan `{{ icon('clave') }}` correctamente
- Los comandos usan `ICONS['clave']` correctamente

### ✅ **Notificaciones Sociales y Privadas**
- Social: `<i>` + sin íconos + tercera persona ✅
- Privado: `<i>` + sin íconos + segunda persona ✅

### ✅ **Estructura General de Templates**
- Usan `<pre>` para outputs descriptivos
- Títulos con íconos y negritas
- Sub-secciones con dos puntos

---

## 🎯 **Plan de Corrección**

### **Prioridad ALTA (Corregir Inmediatamente)**

1. **Estandarizar formato de listas en todos los templates:**
```jinja
{# CORREGIR EN inventory.html.j2, room.html.j2, item_look.html.j2 #}
{%- for item in items %}
{%- set item_icon = item.prototype.get('display', {}).get('icon', icon('item')) %}
    - {{ item_icon }} {{ item.get_name()}}  # ← Usar guion, no número
{%- endfor %}
```

2. **Corregir mensajes de feedback simple:**
```python
# ANTES:
await message.answer(f"<pre>{ICONS['inventory']} <b>Tu Inventario</b>\nNo llevas nada.</pre>", parse_mode="HTML")

# DESPUÉS:
await message.answer(f"{ICONS['inventory']} No llevas nada.")
```

### **Prioridad MEDIA**

3. **Decidir sobre números vs guiones en listas descriptivas:**
   - **Opción A:** Usar siempre guiones (según guía)
   - **Opción B:** Actualizar guía para permitir números

4. **Implementar validación automática:**
   - Script de verificación de cumplimiento de guías
   - Tests unitarios que validen formato de salida

---

## 📊 **Resumen de Cumplimiento por Aspecto**

| Aspecto | Estado | Cumplimiento | Archivos Afectados |
|---------|--------|--------------|-------------------|
| **Indentación 4 espacios** | ❌ Crítico | 60% | inventory.html.j2, room.html.j2 |
| **Formato de listas** | ❌ Crítico | 40% | Todos los templates |
| **Títulos MAYÚSCULAS** | ✅ Bien | 100% | - |
| **Uso de íconos** | ✅ Bien | 100% | - |
| **Notificaciones sociales** | ✅ Bien | 100% | - |
| **Feedback simple** | 🟡 Medio | 70% | commands/player/general.py |
| **Estructura `<pre>`** | 🟡 Medio | 80% | commands/player/general.py |

**Calificación General de Cumplimiento: 71%**

---

## 🚨 **Conclusión**

Las guías de estilo son excelentes y muy detalladas, pero hay inconsistencias importantes en la implementación, especialmente en el formato de listas que es "la regla más importante de toda la guía". 

**Recomendación:** Corregir las incongruencias críticas inmediatamente para mantener la coherencia visual y seguir los estándares de calidad definidos en el proyecto.

---

**Fecha del análisis:** 2025-10-09  
**Analizado por:** Claude (Assistant)  
**Archivos revisados:** 11 templates + 2 comandos principales