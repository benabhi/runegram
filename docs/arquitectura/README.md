# Architecture - Arquitectura del Sistema

Esta sección contiene documentación técnica sobre la arquitectura y estructura del proyecto Runegram.

## 📄 Documentos en esta Sección

### [Configuration System](configuracion.md)
Sistema de configuración híbrido con .env y TOML.

**Temas cubiertos:**
- Filosofía de configuración (credenciales vs. comportamiento)
- Archivo .env (secretos)
- Archivo gameconfig.toml (configuración del juego)
- Sistema de paginación universal
- Límites de visualización
- Agregar nueva configuración
- Validación con Pydantic

**Audiencia:** Desarrolladores y administradores

---

## 🏗️ Conceptos Arquitectónicos Clave

### Separación Motor vs. Contenido
El principio arquitectónico más importante de Runegram:
- **Motor (`src/`):** Código genérico en inglés, reutilizable
- **Contenido (`game_data/`, `commands/`):** Datos específicos del juego en español

Ver [Core Philosophy](../primeros-pasos/filosofia-central.md) para más detalles.

### Stack Tecnológico Principal
- **Python 3.11** + **Aiogram 2.25** (async bot framework)
- **SQLAlchemy 2.0** + **PostgreSQL 15** (ORM y base de datos)
- **Redis 7** (cache y FSM states)
- **Alembic** (migraciones de BD)
- **Docker + Docker Compose** (containerización)
- **APScheduler** (tareas programadas)
- **Jinja2** (templates de output)
- **Pydantic** (validación de configuración)

### Flujo de Datos Típico
```
Usuario → Telegram → Aiogram → Handler → Service → Model → PostgreSQL
                                                      ↓
                                                    Redis (cache)
```

---

## 🎯 Próximos Pasos

Después de entender la arquitectura, explora:
- [Engine Systems](../sistemas-del-motor/) - Sistemas core del motor
- [Content Creation](../creacion-de-contenido/) - Cómo crear contenido

---

**Última actualización:** 2025-10-09
**Estado de la sección:** 🚧 En construcción (2/3 documentos completados)
