# Guía de Base de Datos y Migraciones

La base de datos es la columna vertebral de Runegram, almacenando todo el estado persistente del mundo. La gestión de los cambios en su estructura (el "esquema") se realiza a través de una herramienta llamada **Alembic**. Esta guía explica el concepto y el flujo de trabajo para manejar las migraciones de la base de datos.

## 1. ¿Qué es una Migración?

Cuando cambias el código de un modelo en `src/models/` (por ejemplo, añades una nueva columna `status` a la tabla `Account`), la base de datos no se actualiza mágicamente. Una **migración** es un script de Python que contiene las instrucciones (`ALTER TABLE`, `CREATE TABLE`, etc.) necesarias para llevar la base de datos desde su estado antiguo al nuevo estado que tus modelos definen.

Alembic se encarga de generar y ejecutar estos scripts de forma ordenada.

## 2. El Flujo de Trabajo para Cambios en los Modelos

Cada vez que realices un cambio en la estructura de un modelo, debes seguir este proceso para que el cambio se refleje correctamente en la base de datos.

### Paso 1: Modificar el Modelo de Python

Realiza los cambios necesarios en el archivo del modelo correspondiente en `src/models/`.

**Ejemplo:** Añadir una columna `nickname` a la tabla `characters`.

```python
# En src/models/character.py
class Character(Base):
    # ...
    name = Column(String(50), unique=True, nullable=False)
    nickname = Column(String(50), nullable=True) # <-- NUEVA COLUMNA
    # ...
```

### Paso 2: Generar el Script de Migración

Una vez guardados los cambios en el modelo, necesitas que Alembic compare tus modelos actualizados con el estado actual de la base de datos y genere el script de migración.

1.  **Asegúrate de que tus contenedores estén en ejecución:**
    ```bash
    docker-compose up -d
    ```

2.  **Ejecuta el comando `autogenerate`:**
    Usa `docker-compose exec` para ejecutar Alembic dentro del contenedor del bot. Proporciona siempre un mensaje descriptivo con `-m`.

    ```bash
    docker-compose exec bot alembic revision --autogenerate -m "Añadir columna nickname a characters"
    ```

Alembic generará un nuevo archivo en `alembic/versions/` con un nombre como `xxxxxxxxxxxx_añadir_columna_nickname_a_characters.py`.

### Paso 3: Revisar y Corregir el Script (¡Paso Crucial!)

El comando `autogenerate` es una herramienta potente, pero **no es perfecto**. A veces puede interpretar los cambios de forma incorrecta o añadir operaciones no deseadas.

**Siempre debes abrir el nuevo archivo de migración y revisarlo.**

**Caso Común de Error: Tablas Externas**
Alembic solo conoce los modelos definidos en `src/models/`. Si tienes una tabla creada "manualmente" por una migración (como `apscheduler_jobs`), `autogenerate` la verá en la base de datos pero no en los modelos y pensará que debe ser eliminada.

**Si ves líneas como `op.drop_table('apscheduler_jobs')` o `op.drop_index(...)` en una migración que no debería afectar a esa tabla, ¡bórralas del archivo!**

### Paso 4: Aplicar la Migración

Una vez que has revisado y estás conforme con el script de migración, puedes aplicarlo. En el entorno de desarrollo, la forma más simple y segura es reiniciar todo el sistema con el script de reseteo.

```bash
# En Windows
scripts\full_reset.bat```

Este script detendrá los contenedores, borrará la base de datos antigua y la reconstruirá desde cero, aplicando **todas** las migraciones en orden, incluida la nueva que acabas de crear. Al arrancar, el `entrypoint.sh` se encarga de ejecutar `alembic upgrade head`, que pone la base de datos al día.

## 3. Comandos Útiles de Alembic

Puedes ejecutar estos comandos usando `docker-compose exec bot alembic <comando>`.

*   `alembic current`: Muestra el ID de la última migración aplicada a la base de datos.
*   `alembic heads`: Muestra el ID de la migración más reciente en tus archivos (la "cabeza" o `head`).
*   `alembic history`: Muestra el historial de todas las migraciones, desde la base hasta la cabeza, indicando cuál es la actual.
*   `alembic upgrade head`: Aplica todas las migraciones pendientes.
*   `alembic downgrade -1`: Revierte la última migración aplicada. (Usar con cuidado).