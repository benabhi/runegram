# Tests de Runegram MUD

Esta carpeta contiene la suite completa de tests automatizados del proyecto.

## Estructura

```
tests/
├── __init__.py                 # Inicialización del paquete de tests
├── conftest.py                 # Fixtures compartidas y configuración de pytest
├── test_services/              # Tests para servicios de negocio
│   ├── test_validation_service.py
│   └── test_permission_service.py
├── test_commands/              # Tests para comandos del juego
│   └── (por implementar)
└── test_systems/               # Tests para sistemas core del motor
    └── (por implementar)
```

## Ejecutar Tests

### Todos los tests
```bash
pytest
```

### Tests específicos
```bash
# Por archivo
pytest tests/test_services/test_validation_service.py

# Por clase
pytest tests/test_services/test_permission_service.py::TestRoleLock

# Por función específica
pytest tests/test_services/test_permission_service.py::TestRoleLock::test_admin_can_access_admin_commands
```

### Tests por categoría
```bash
# Solo tests críticos
pytest -m critical

# Excluir tests lentos
pytest -m "not slow"

# Solo tests de integración
pytest -m integration
```

### Con cobertura
```bash
# Ejecutar tests y generar reporte de cobertura
pytest --cov=src --cov-report=html

# Ver reporte en navegador
open htmlcov/index.html  # Linux/Mac
start htmlcov/index.html  # Windows
```

### Opciones útiles
```bash
# Modo verboso (muestra cada test)
pytest -v

# Detener al primer fallo
pytest -x

# Mostrar output de print()
pytest -s

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest -n auto
```

## Escribir Tests

### Estructura básica

```python
import pytest

@pytest.mark.asyncio  # Para tests asíncronos
class TestMiFeature:
    """Descripción de qué estamos testeando."""

    async def test_caso_exitoso(self, db_session):
        """Test: Descripción del caso de éxito."""
        # Arrange
        # ... preparar datos

        # Act
        # ... ejecutar la acción

        # Assert
        assert resultado_esperado, "Mensaje descriptivo si falla"

    async def test_caso_error(self, db_session):
        """Test: Descripción del caso de error."""
        with pytest.raises(MiExcepcion):
            # código que debería lanzar excepción
            pass
```

### Usar fixtures

Las fixtures están definidas en `conftest.py` y están disponibles automáticamente:

```python
async def test_con_fixtures(
    db_session,           # Sesión de BD en memoria
    sample_character,     # Personaje de prueba
    sample_room,          # Sala de prueba
    admin_character       # Personaje admin
):
    # Usar las fixtures directamente
    assert sample_character.name == "TestCharacter"
```

### Marcar tests

```python
@pytest.mark.critical  # Test crítico
@pytest.mark.slow      # Test lento
@pytest.mark.integration  # Test de integración
async def test_importante():
    pass
```

## Categorías de Tests

### Tests Críticos (@critical)
Tests que validan funcionalidad esencial del juego. **Deben pasar siempre** antes de hacer commit.

Ejemplos:
- Sistema de permisos
- Sistema de validación
- Creación de personajes
- Comandos básicos de movimiento

### Tests de Integración (@integration)
Tests que verifican la interacción entre múltiples componentes.

Ejemplos:
- Flujo completo de crear personaje → mover → coger objeto
- Sistema de combate completo
- Broadcast de mensajes sociales

### Tests Lentos (@slow)
Tests que tardan más de 1 segundo. Pueden saltarse durante desarrollo para feedback rápido.

Ejemplos:
- Tests que crean muchas entidades
- Tests que simulan tickers a largo plazo

## Fixtures Disponibles

### Bases de Datos
- `db_session`: Sesión de BD en memoria (SQLite)

### Entidades
- `sample_room`: Sala de prueba
- `sample_account`: Cuenta de jugador
- `sample_character`: Personaje de jugador
- `admin_account`: Cuenta de administrador
- `admin_character`: Personaje administrador
- `sample_item`: Item de prueba

Ver `conftest.py` para la lista completa y detalles.

## Cobertura de Código

El objetivo es mantener una cobertura de código alta (>70%) en áreas críticas:

✅ **Alta prioridad (>80%):**
- `src/services/permission_service.py`
- `src/services/validation_service.py`
- `src/services/player_service.py`
- `commands/player/movement.py`

⚠️ **Media prioridad (>60%):**
- Otros servicios
- Comandos de jugador
- Sistemas core

⏸️ **Baja prioridad:**
- Scripts específicos de contenido
- Tickers de items individuales

## Mejores Prácticas

### 1. Nombres descriptivos
```python
# ❌ Malo
def test_1():
    pass

# ✅ Bueno
def test_admin_can_access_admin_commands():
    """Test: ADMIN debería poder ejecutar comandos que requieren rol(ADMIN)."""
    pass
```

### 2. Un concepto por test
```python
# ❌ Malo - mezcla múltiples conceptos
def test_permissions():
    # Testea rol
    # Testea items
    # Testea operadores booleanos
    pass

# ✅ Bueno - un test por concepto
def test_rol_lock():
    pass

def test_tiene_objeto_lock():
    pass

def test_and_operator():
    pass
```

### 3. Arrange-Act-Assert
```python
def test_algo():
    # Arrange: Preparar
    character = crear_personaje()

    # Act: Ejecutar
    resultado = hacer_algo(character)

    # Assert: Verificar
    assert resultado == esperado
```

### 4. Tests independientes
Cada test debe poder ejecutarse solo, sin depender del orden o estado de otros tests.

### 5. Datos de prueba realistas
```python
# ❌ Malo
account = Account(telegram_id=1)

# ✅ Bueno
account = Account(telegram_id=999999)  # Claramente un ID de test
```

## Integración Continua

Los tests se ejecutan automáticamente:
- En cada commit (pre-commit hook recomendado)
- En cada pull request
- Antes de cada deploy

Ver `CLAUDE.md` para las políticas de tests del proyecto.

## Troubleshooting

### Tests fallan localmente pero pasan en CI
- Verificar que las dependencias están actualizadas: `pip install -r requirements.txt`
- Limpiar caché de pytest: `pytest --cache-clear`

### Tests asíncronos no funcionan
- Verificar que tiene el decorator `@pytest.mark.asyncio`
- Verificar que `pytest-asyncio` está instalado

### Cobertura incorrecta
- Limpiar archivos de cobertura anteriores: `rm -rf .coverage htmlcov/`
- Ejecutar de nuevo con `--cov-report=html`

## Recursos

- [Documentación de Pytest](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Pytest-cov](https://pytest-cov.readthedocs.io/)
