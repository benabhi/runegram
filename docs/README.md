# Documentación de Runegram MUD

Bienvenido a la documentación completa de Runegram, un motor de juego de rol textual multijugador (MUD) diseñado para Telegram.

## 📚 Estructura de la Documentación

La documentación está organizada en secciones lógicas para facilitar la navegación:

### 🚀 [Getting Started](getting-started/) - Primeros Pasos
Documentación para nuevos desarrolladores y jugadores.

- **[Installation](getting-started/installation.md)** - Configuración del entorno de desarrollo
- **[Core Philosophy](getting-started/core-philosophy.md)** - Filosofía y principios de diseño
- **[Quick Reference](getting-started/quick-reference.md)** - Referencia rápida de conceptos clave
- **[Glossary](getting-started/glossary.md)** - Glosario de términos técnicos

### 🏗️ [Architecture](architecture/) - Arquitectura del Sistema
Documentación técnica sobre la estructura del proyecto.

- **[Overview](architecture/overview.md)** - Visión general de la arquitectura
- **[Database and Migrations](architecture/database-migrations.md)** - Sistema de base de datos y Alembic
- **[Configuration System](architecture/configuration.md)** - Sistema de configuración híbrido (.env + TOML)

### ⚙️ [Engine Systems](engine-systems/) - Sistemas del Motor
Documentación detallada de los sistemas core del motor.

- **[Command System](engine-systems/command-system.md)** - Sistema de comandos dinámico
- **[Permission System](engine-systems/permission-system.md)** - Sistema de locks y permisos
- **[Prototype System](engine-systems/prototype-system.md)** - Sistema data-driven de prototipos
- **[Scripting Engine](engine-systems/scripting-engine.md)** - Motor de scripts Python
- **[Validation System](engine-systems/validation-system.md)** - Sistema de validación de integridad
- **[Pulse System](engine-systems/pulse-system.md)** - Sistema de pulso temporal global
- **[Broadcaster Service](engine-systems/broadcaster-service.md)** - Sistema de broadcasting de mensajes
- **[Online Presence System](engine-systems/online-presence.md)** - Sistema de presencia online/offline
- **[Channels System](engine-systems/channels-system.md)** - Sistema de canales de comunicación
- **[Narrative Service](engine-systems/narrative-service.md)** - Mensajes evocativos aleatorios
- **[Item Disambiguation](engine-systems/item-disambiguation.md)** - Sistema de ordinales para objetos duplicados
- **[Categories and Tags](engine-systems/categories-tags.md)** - Sistema de categorización y etiquetado

### 🎨 [Content Creation](content-creation/) - Creación de Contenido
Guías para diseñadores de contenido y builders.

- **[Creating Commands](content-creation/creating-commands.md)** - Cómo crear nuevos comandos
- **[Creating Rooms](content-creation/creating-rooms.md)** - Construir salas y mundos
- **[Creating Items](content-creation/creating-items.md)** - Diseñar objetos y prototipos
- **[Writing Scripts](content-creation/writing-scripts.md)** - Escribir scripts de comportamiento
- **[Output Style Guide](content-creation/output-style-guide.md)** - Guía de estilo para outputs
- **[Categories and Tags Guide](content-creation/categories-tags-guide.md)** - Guía de uso de categories/tags
- **[Inline Buttons](content-creation/inline-buttons.md)** - Sistema de botones inline de Telegram

### 👨‍💼 [Admin Guide](admin-guide/) - Guía de Administración
Documentación para administradores del juego.

- **[Admin Commands](admin-guide/admin-commands.md)** - Referencia de comandos de administración
- **[Troubleshooting](admin-guide/troubleshooting.md)** - Resolución de problemas comunes

### 🎮 [Player Guide](player-guide/) - Guía de Jugador
Documentación para jugadores del juego.

- **[Getting Started](player-guide/getting-started-player.md)** - Cómo empezar a jugar
- **[Command Reference](player-guide/command-reference.md)** - Referencia completa de comandos de jugador

### 📖 [Reference](reference/) - Material de Referencia
Referencias técnicas completas.

- **[Complete Command Reference](reference/complete-command-reference.md)** - Referencia exhaustiva de todos los comandos
- **[API Reference](reference/api-reference.md)** - Referencia de APIs y servicios

### 🗺️ [Roadmap](roadmap/) - Hoja de Ruta
Planificación y sistemas futuros.

- **[Vision and Roadmap](roadmap/vision.md)** - Visión a largo plazo del proyecto
- **[Combat System](roadmap/combat-system.md)** - Sistema de combate planificado (futuro)
- **[Skill System](roadmap/skill-system.md)** - Sistema de habilidades planificado (futuro)

---

## 🔍 Navegación Rápida

### Para Desarrolladores Nuevos
1. Empieza con [Installation](getting-started/installation.md)
2. Lee [Core Philosophy](getting-started/core-philosophy.md)
3. Consulta [Quick Reference](getting-started/quick-reference.md)
4. Explora [Engine Systems](engine-systems/)

### Para Creadores de Contenido
1. Lee [Core Philosophy](getting-started/core-philosophy.md)
2. Consulta [Creating Rooms](content-creation/creating-rooms.md)
3. Consulta [Creating Items](content-creation/creating-items.md)
4. Lee [Output Style Guide](content-creation/output-style-guide.md)

### Para Administradores
1. Consulta [Admin Commands](admin-guide/admin-commands.md)
2. Lee [Troubleshooting](admin-guide/troubleshooting.md)
3. Familiarízate con [Complete Command Reference](reference/complete-command-reference.md)

### Para Jugadores
1. Empieza con [Getting Started](player-guide/getting-started-player.md)
2. Consulta [Command Reference](player-guide/command-reference.md) cuando necesites ayuda

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

**Versión:** 2.0
**Última actualización:** 2025-10-09
**Estado:** ✅ Reestructuración completa

### Changelog de Estructura
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
