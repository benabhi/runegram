#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recrear prompt.md con codificación UTF-8 correcta.
"""

content = """# 🧹 Plan de Limpieza y Actualización de Runegram

**Fecha:** 2025-10-17
**Versión:** 1.0
**Objetivo:** Realizar una limpieza integral del código y documentación del proyecto Runegram para mantenerlo consistente, moderno y alineado con su estado actual (Sistema de Scripts v2.0).

---

## 📊 Resumen Ejecutivo

### Estado Actual del Proyecto
- **Código fuente:** ✅ En excelente estado (v2.0, arquitectura limpia)
- **Documentación:** ⚠️ Inconsistencias detectadas (~15% desactualizado)
- **Archivos obsoletos:** ⚠️ Bytecode obsoleto de `pulse_service.py` en `__pycache__`
- **Calidad del código:** ✅ Alta (sin redundancias significativas, separación motor/contenido impecable)

### Hallazgos Principales

#### ✅ Fortalezas del Proyecto
1. **Arquitectura sólida y moderna**: Sistema de Scripts v2.0 completamente implementado
2. **Separación motor/contenido**: Impecable (inglés/español, genérico/específico)
3. **Sin código duplicado**: No hay redundancias críticas
4. **18 servicios bien definidos**: Responsabilidades claras y separadas
5. **Comandos migrados**: Sistema de eventos BEFORE/AFTER implementado en 6 comandos

#### ⚠️ Problemas Detectados

**CÓDIGO (Prioridad Media)**
1. 1 archivo bytecode obsoleto: `pulse_service.cpython-311.pyc`
2. 2 comentarios en código mencionando `pulse_service` (documentación interna)
3. 1 TODO pendiente en `src/utils/inline_keyboards.py` (funcionalidad futura)

**DOCUMENTACIÓN (Prioridad Alta)**
1. **12 referencias a `pulse_service` eliminado** en 4 archivos de documentación
2. **1 documento crítico desactualizado**: `escritura-de-scripts.md` (v1.0 vs código v2.0)
3. **Contenido en inglés**: `docs/README.md` (títulos y YAML frontmatter)
4. **Enlaces rotos**: Referencias a `sistema-de-pulso.md` (no existe)

---

## 🎯 Plan de Acción Detallado

### FASE 1: Limpieza Crítica de Documentación (PRIORIDAD ALTA)

#### 1.1. Eliminar Referencias a `pulse_service`

**Archivos a modificar:**

| Archivo | Líneas | Tipo de cambio | Tiempo estimado |
|---------|--------|----------------|-----------------|
| `CLAUDE.md` | 352 | Reemplazar `pulse_service.py` → `scheduler_service.py` | 2 min |
| `docs/README.md` | 29 | Reemplazar `sistema-de-pulso.md` → `sistema-de-scheduling.md` | 2 min |
| `docs/sistemas-del-motor/README.md` | 171, 352 | Reemplazar referencias a pulse | 5 min |
| `docs/creacion-de-contenido/escritura-de-scripts.md` | 10, 93, 166 | Reemplazar enlaces rotos | 5 min |

**Cambios específicos:**

```markdown
# ANTES (INCORRECTO)
- **[Pulse System](sistemas-del-motor/sistema-de-pulso.md)** - Sistema de pulso temporal global
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-pulso.md"

# DESPUÉS (CORRECTO)
- **[Sistema de Scheduling](sistemas-del-motor/sistema-de-scheduling.md)** - Sistema de scheduling híbrido (tick + cron)
documentos_relacionados:
  - "sistemas-del-motor/sistema-de-scheduling.md"
```

**Responsable:** Agente `runegram-docs-keeper`
**Verificación:** Buscar `pulse_service` y `sistema-de-pulso` en toda la documentación

---

#### 1.2. Actualizar `escritura-de-scripts.md` a v2.0

**Archivo:** `docs/creacion-de-contenido/escritura-de-scripts.md`
**Estado actual:** v1.0 (obsoleto)
**Estado deseado:** v2.0 (actual)

**Opción A: Reescritura Completa (Recomendado)**

Agregar las siguientes secciones faltantes:

1. **Sistema de Eventos v2.0** (BEFORE/AFTER)
   - Eventos disponibles (16 tipos)
   - Prioridades
   - Cancelación de acciones
   - Ejemplos con `event_service`

2. **Scheduling v2.0** (Cron + Tick)
   - `tick_scripts` (v1.0 retrocompatible)
   - `scheduled_scripts` (v2.0 nuevo)
   - Cron expressions
   - Scripts globales vs por jugador

3. **Sistema de Estado v2.0**
   - Estado persistente (PostgreSQL JSONB)
   - Estado transiente (Redis TTL)
   - Cooldowns
   - Ejemplos con `state_service`

4. **Ejemplos Actualizados**
   - Item con evento BEFORE (cancelación)
   - Item con evento AFTER (efectos)
   - Item con cron schedule
   - Item con cooldowns

**Opción B: Advertencia Temporal (Rápido)**

Agregar advertencia prominente al inicio:

```markdown
> ⚠️ **ADVERTENCIA: Documento Desactualizado**
> Este documento describe el Sistema de Scripts v1.0.
> Para información actualizada sobre v2.0 (eventos, cron, estado), consultar:
> - [Sistema de Scripts v2.0](../sistemas-del-motor/sistema-de-scripts.md)
> - [Sistema de Eventos v2.0](../sistemas-del-motor/sistema-de-eventos.md)
> - [Sistema de Scheduling v2.0](../sistemas-del-motor/sistema-de-scheduling.md)
> - [Sistema de Estado v2.0](../sistemas-del-motor/sistema-de-estado.md)
```

**Recomendación:** Opción A (reescritura) para mantener documentación de alta calidad.
**Tiempo estimado:** 2-3 horas (Opción A) vs 5 minutos (Opción B)

---

## 📝 Verificación de Codificación de Archivos

### Política de Codificación (NUEVO)

**IMPORTANTE**: Este proyecto ha tenido problemas recurrentes con codificación de archivos. Todos los archivos de texto deben usar **UTF-8 sin BOM**.

#### Verificación Obligatoria Antes de Commit

**Comando para verificar codificación:**
```bash
# Verificar codificación de archivos específicos
file -i prompt.md
file -i CLAUDE.md
file -i docs/**/*.md

# Verificar todos los archivos markdown
find . -name "*.md" -exec file -i {} \\;
```

#### Corrección de Problemas de Codificación

**Script de corrección automática:**
```bash
# Convertir archivo a UTF-8
iconv -f WINDOWS-1252 -t UTF-8 archivo.md -o archivo_fixed.md

# O con Python (más confiable)
python -c "
with open('archivo.md', 'r', encoding='latin-1') as f:
    content = f.read()
with open('archivo.md', 'w', encoding='utf-8') as f:
    f.write(content)
"
```

#### Configuración de Editor

**VS Code (.vscode/settings.json):**
```json
{
  "files.encoding": "utf8",
  "files.autoGuessEncoding": false,
  "files.eol": "\\n"
}
```

**Verificación en Python:**
```python
import chardet

def verify_encoding(filepath):
    with open(filepath, 'rb') as f:
        result = chardet.detect(f.read())
        print(f"{filepath}: {result['encoding']} (confidence: {result['confidence']})")
        if result['encoding'].lower() not in ['utf-8', 'ascii']:
            print(f"⚠️ WARNING: {filepath} no está en UTF-8!")
            return False
    return True

# Verificar todos los markdown
import glob
for md_file in glob.glob('**/*.md', recursive=True):
    verify_encoding(md_file)
```

---

**Última actualización:** 2025-10-17
**Autor:** Claude Code (Análisis exhaustivo)
**Basado en:** Análisis de 126 archivos Python + 46 archivos markdown
**Estado:** ✅ Plan completo y listo para ejecución
"""

if __name__ == "__main__":
    import os
    from pathlib import Path

    # Guardar en la raíz del proyecto
    project_root = Path(__file__).parent.parent
    output_file = project_root / "prompt.md"

    with open(output_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

    print(f"✅ Archivo recreado correctamente en: {output_file}")
    print(f"📏 Tamaño: {len(content)} caracteres")
    print(f"🔤 Codificación: UTF-8")
