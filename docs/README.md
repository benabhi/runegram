# Documentación de Runegram MUD

Bienvenido a la documentación completa de Runegram, un motor de juego de rol textual multijugador (MUD) diseñado para Telegram.

## 📚 Estructura de la Documentación

La documentación está organizada en secciones lógicas para facilitar la navegación:

### 🚀 [Getting Started](primeros-pasos/) - Primeros Pasos
Documentación para nuevos desarrolladores y jugadores.

- **[Installation](primeros-pasos/instalacion.md)** - Configuración del entorno de desarrollo
- **[Core Philosophy](primeros-pasos/filosofia-central.md)** - Filosofía y principios de diseño

### 🏗️ [Architecture](arquitectura/) - Arquitectura del Sistema
Documentación técnica sobre la estructura del proyecto.

- **[Configuration System](arquitectura/configuracion.md)** - Sistema de configuración híbrido (.env + TOML)

### ⚙️ [Engine Systems](sistemas-del-motor/) - Sistemas del Motor
Documentación detallada de los sistemas core del motor.

- **[Command System](sistemas-del-motor/sistema-de-comandos.md)** - Sistema de comandos dinámico
- **[Permission System](sistemas-del-motor/sistema-de-permisos.md)** - Sistema de locks y permisos
- **[Prototype System](sistemas-del-motor/sistema-de-prototipos.md)** - Sistema data-driven de prototipos
- **[Scripting Engine](sistemas-del-motor/sistema-de-scripts.md)** - Motor de scripts Python
- **[Validation System](sistemas-del-motor/sistema-de-validacion.md)** - Sistema de validación de integridad
- **[Ban and Appeal System](sistemas-del-motor/sistema-de-baneos.md)** - Sistema de baneos y apelaciones
- **[Pulse System](sistemas-del-motor/sistema-de-pulso.md)** - Sistema de pulso temporal global
- **[Online Presence System](sistemas-del-motor/presencia-en-linea.md)** - Sistema de presencia online/offline
- **[Channels System](sistemas-del-motor/sistema-de-canales.md)** - Sistema de canales de comunicación
- **[Narrative Service](sistemas-del-motor/sistema-de-narrativa.md)** - Mensajes evocativos aleatorios
- **[Item Disambiguation](sistemas-del-motor/desambiguacion-de-items.md)** - Sistema de ordinales para objetos duplicados
- **[Social Systems](sistemas-del-motor/sistemas-sociales.md)** - Sistemas de interacción social
- **[Categories and Tags](sistemas-del-motor/categorias-y-etiquetas.md)** - Sistema de categorización y etiquetado
- **[Inline Buttons](sistemas-del-motor/botones-en-linea.md)** - Sistema de botones inline de Telegram

### 🎨 [Content Creation](creacion-de-contenido/) - Creación de Contenido
Guías para diseñadores de contenido y builders.

- **[Creating Commands](creacion-de-contenido/creacion-de-comandos.md)** - Cómo crear nuevos comandos
- **[Creating Rooms](creacion-de-contenido/construccion-de-salas.md)** - Construir salas y mundos
- **[Creating Items](creacion-de-contenido/creacion-de-items.md)** - Diseñar objetos y prototipos
- **[Writing Scripts](creacion-de-contenido/escritura-de-scripts.md)** - Escribir scripts de comportamiento
- **[Output Style Guide](creacion-de-contenido/guia-de-estilo-de-salida.md)** - Guía de estilo para outputs

### 👨‍💼 [Admin Guide](guia-de-administracion/) - Guía de Administración
Documentación para administradores del juego.

- **[Admin Commands](guia-de-administracion/comandos-de-administracion.md)** - Referencia de comandos de administración
- **[Database Migrations](guia-de-administracion/migraciones-de-base-de-datos.md)** - Sistema de base de datos y Alembic

### 📖 [Reference](referencia/) - Material de Referencia
Referencias técnicas completas.

- **[Complete Command Reference](referencia/referencia-de-comandos.md)** - Referencia exhaustiva de todos los comandos

### 🗺️ [Roadmap](hoja-de-ruta/) - Hoja de Ruta
Planificación y sistemas futuros.

- **[Vision and Goals](hoja-de-ruta/vision-y-objetivos.md)** - Visión a largo plazo del proyecto
- **[Planned Features](hoja-de-ruta/funcionalidades-planificadas.md)** - Funcionalidades planificadas
- **[Combat System](hoja-de-ruta/diseno-sistema-de-combate.md)** - Sistema de combate planificado (futuro)
- **[Skill System](hoja-de-ruta/diseno-sistema-de-habilidades.md)** - Sistema de habilidades planificado (futuro)

---

## 🔍 Navegación Rápida

### Para Desarrolladores Nuevos
1. Empieza con [Installation](primeros-pasos/instalacion.md)
2. Lee [Core Philosophy](primeros-pasos/filosofia-central.md)
3. Explora [Engine Systems](sistemas-del-motor/)

### Para Creadores de Contenido
1. Lee [Core Philosophy](primeros-pasos/filosofia-central.md)
2. Consulta [Creating Rooms](creacion-de-contenido/construccion-de-salas.md)
3. Consulta [Creating Items](creacion-de-contenido/creacion-de-items.md)
4. Lee [Output Style Guide](creacion-de-contenido/guia-de-estilo-de-salida.md)

### Para Administradores
1. Consulta [Admin Commands](guia-de-administracion/comandos-de-administracion.md)
2. Familiarízate con [Complete Command Reference](referencia/referencia-de-comandos.md)

---

## 📝 Convenciones de Documentación

### YAML Frontmatter
Todos los archivos de documentación incluyen metadatos YAML frontmatter:

```yaml
---
title: "Título del Documento"
category: "Getting Started" | "Architecture" | "Engine Systems" | etc.
version: "1.0"
last_updated: "YYYY-MM-DD"
author: "Runegram Project"
tags: ["tag1", "tag2"]
related_docs:
  - "ruta/relativa/documento.md"
code_references:
  - "src/services/example_service.py"
status: "current" | "draft" | "deprecated"
---
```

### Estados de Documentación
- **current**: Documentación actualizada y precisa
- **draft**: Documentación en progreso
- **deprecated**: Documentación obsoleta (marcada para revisión/eliminación)

### Íconos y Emojis
Los emojis se usan estratégicamente para facilitar el escaneo visual:
- 🎯 Objetivo/Meta
- 🚨 Advertencia crítica
- ✅ Correcto/Bueno
- ❌ Incorrecto/Malo
- 📚 Referencia
- ⚠️ Precaución
- 🔧 Configuración
- 💡 Consejo

---

## 🤝 Contribuir a la Documentación

### Principios
1. **Documentación debe estar sincronizada con el código**
2. **Usa ejemplos del código real**
3. **Mantén consistencia con CLAUDE.md**
4. **Actualiza frontmatter (version, last_updated)**
5. **Verifica enlaces internos**

### Workflow
1. Modifica el archivo de documentación
2. Actualiza `version` y `last_updated` en frontmatter
3. Verifica enlaces internos
4. Commit con mensaje descriptivo

---

## 📊 Estado de la Documentación

**Versión:** 2.1
**Última actualización:** 2025-01-11
**Estado:** ✅ Actualizado con sistema de baneos

### Changelog de Estructura
- **v2.1 (2025-01-11)**: Agregado sistema de baneos y apelaciones
- **v2.0 (2025-10-09)**: Reestructuración completa con nueva jerarquía de directorios y YAML frontmatter
- **v1.0 (2025-01-09)**: Estructura original con numeración prefijada

---

## 🔗 Enlaces Externos

- [Aiogram 2.x Docs](https://docs.aiogram.dev/en/v2.25.1/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [TOML Specification](https://toml.io/)
- [Pydantic Settings](https://docs.pydantic.dev/usage/settings/)

---

**Mantenedor:** Proyecto Runegram
**Repositorio:** https://github.com/tu-usuario/runegram
