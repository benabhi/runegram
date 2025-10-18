# Documentación de Runegram MUD

Bienvenido a la documentación completa de Runegram, un motor de juego de rol textual multijugador (MUD) diseñado para Telegram.

## 📚 Estructura de la Documentación

La documentación está organizada en secciones lógicas para facilitar la navegación:

### 🚀 [Primeros Pasos](primeros-pasos/)
Documentación para nuevos desarrolladores y jugadores.

- **[Instalación](primeros-pasos/instalacion.md)** - Configuración del entorno de desarrollo
- **[Filosofía Central](primeros-pasos/filosofia-central.md)** - Filosofía y principios de diseño

### 🏗️ [Arquitectura](arquitectura/)
Documentación técnica sobre la estructura del proyecto.

- **[Sistema de Configuración](arquitectura/configuracion.md)** - Sistema de configuración híbrido (.env + TOML)

### ⚙️ [Sistemas del Motor](sistemas-del-motor/)
Documentación detallada de los sistemas core del motor.

- **[Sistema de Comandos](sistemas-del-motor/sistema-de-comandos.md)** - Sistema de comandos dinámico
- **[Sistema de Permisos](sistemas-del-motor/sistema-de-permisos.md)** - Sistema de locks y permisos
- **[Sistema de Prototipos](sistemas-del-motor/sistema-de-prototipos.md)** - Sistema data-driven de prototipos
- **[Motor de Scripts](sistemas-del-motor/sistema-de-scripts.md)** - Motor de scripts Python v2.0
- **[Sistema de Eventos](sistemas-del-motor/sistema-de-eventos.md)** - Sistema de eventos BEFORE/AFTER
- **[Sistema de Scheduling](sistemas-del-motor/sistema-de-scheduling.md)** - Sistema de scheduling (tick + cron)
- **[Sistema de Estado](sistemas-del-motor/sistema-de-estado.md)** - Gestión de estado persistente y transiente
- **[Sistema de Validación](sistemas-del-motor/sistema-de-validacion.md)** - Sistema de validación de integridad
- **[Sistema de Baneos](sistemas-del-motor/sistema-de-baneos.md)** - Sistema de baneos y apelaciones
- **[Sistema de Presencia Online](sistemas-del-motor/presencia-en-linea.md)** - Sistema de presencia online/offline
- **[Sistema de Canales](sistemas-del-motor/sistema-de-canales.md)** - Sistema de canales de comunicación
- **[Servicio de Narrativa](sistemas-del-motor/sistema-de-narrativa.md)** - Mensajes evocativos aleatorios
- **[Desambiguación de Items](sistemas-del-motor/desambiguacion-de-items.md)** - Sistema de ordinales para objetos duplicados
- **[Sistemas Sociales](sistemas-del-motor/sistemas-sociales.md)** - Sistemas de interacción social
- **[Categorías y Etiquetas](sistemas-del-motor/categorias-y-etiquetas.md)** - Sistema de categorización y etiquetado
- **[Botones Inline](sistemas-del-motor/botones-en-linea.md)** - Sistema de botones inline de Telegram
- **[Servicio de Broadcasting](sistemas-del-motor/servicio-de-broadcasting.md)** - Sistema de mensajería a salas y personajes

### 🎨 [Creación de Contenido](creacion-de-contenido/)
Guías para diseñadores de contenido y builders.

- **[Creación de Comandos](creacion-de-contenido/creacion-de-comandos.md)** - Cómo crear nuevos comandos
- **[Construcción de Salas](creacion-de-contenido/construccion-de-salas.md)** - Construir salas y mundos
- **[Creación de Items](creacion-de-contenido/creacion-de-items.md)** - Diseñar objetos y prototipos
- **[Escritura de Scripts](creacion-de-contenido/escritura-de-scripts.md)** - Escribir scripts de comportamiento
- **[Guía de Estilo de Salida](creacion-de-contenido/guia-de-estilo-de-salida.md)** - Guía de estilo para outputs

### 👨‍💼 [Guía de Administración](guia-de-administracion/)
Documentación para administradores del juego.

- **[Comandos de Administración](guia-de-administracion/comandos-de-administracion.md)** - Referencia de comandos de administración
- **[Migraciones de Base de Datos](guia-de-administracion/migraciones-de-base-de-datos.md)** - Sistema de base de datos y Alembic

### 📖 [Referencia](referencia/)
Referencias técnicas completas.

- **[Referencia Completa de Comandos](referencia/referencia-de-comandos.md)** - Referencia exhaustiva de todos los comandos

### 🗺️ [Hoja de Ruta](hoja-de-ruta/)
Planificación y sistemas futuros.

- **[Visión y Objetivos](hoja-de-ruta/vision-y-objetivos.md)** - Visión a largo plazo del proyecto
- **[Funcionalidades Planificadas](hoja-de-ruta/funcionalidades-planificadas.md)** - Funcionalidades planificadas
- **[Sistema de Combate](hoja-de-ruta/diseno-sistema-de-combate.md)** - Sistema de combate planificado (futuro)
- **[Sistema de Habilidades](hoja-de-ruta/diseno-sistema-de-habilidades.md)** - Sistema de habilidades planificado (futuro)

---

## 🔍 Navegación Rápida

### Para Desarrolladores Nuevos
1. Empieza con [Instalación](primeros-pasos/instalacion.md)
2. Lee [Filosofía Central](primeros-pasos/filosofia-central.md)
3. Explora [Sistemas del Motor](sistemas-del-motor/)

### Para Creadores de Contenido
1. Lee [Filosofía Central](primeros-pasos/filosofia-central.md)
2. Consulta [Construcción de Salas](creacion-de-contenido/construccion-de-salas.md)
3. Consulta [Creación de Items](creacion-de-contenido/creacion-de-items.md)
4. Lee [Guía de Estilo de Salida](creacion-de-contenido/guia-de-estilo-de-salida.md)

### Para Administradores
1. Consulta [Comandos de Administración](guia-de-administracion/comandos-de-administracion.md)
2. Familiarízate con [Referencia Completa de Comandos](referencia/referencia-de-comandos.md)

---

## 📝 Convenciones de Documentación

### YAML Frontmatter
Todos los archivos de documentación incluyen metadatos YAML frontmatter:

```yaml
---
título: "Título del Documento"
categoría: "Comenzando" | "Arquitectura" | "Sistemas del Motor" | etc.
última_actualización: "YYYY-MM-DD"
autor: "Proyecto Runegram"
etiquetas: ["etiqueta1", "etiqueta2"]
documentos_relacionados:
  - "ruta/relativa/documento.md"
referencias_código:
  - "src/services/example_service.py"
estado: "actual" | "borrador"
importancia: "alta" | "crítica" | "normal"
audiencia: "desarrollador" | "creador-de-contenido" | "admin" | "jugador" | "todos"
---
```

### Estados de Documentación
- **actual**: Documentación actualizada y precisa
- **borrador**: Documentación en progreso

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

**Última actualización:** 2025-10-17
**Estado:** ✅ Actualizado con sistema de scripts completo y traducción completa al español

### Changelog de Estructura
- **2025-10-17**: Sistema de scripts (eventos, scheduling, estado), eliminación de pulse_service, traducción completa al español
- **2025-01-11**: Agregado sistema de baneos y apelaciones
- **2025-10-09**: Reestructuración completa con nueva jerarquía de directorios y YAML frontmatter
- **2025-01-09**: Estructura original con numeración prefijada

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
