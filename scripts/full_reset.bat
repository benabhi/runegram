@ECHO OFF
CLS
ECHO.
ECHO ##################################################################
ECHO #            SCRIPT DE REINICIO COMPLETO PARA RUNEGRAM           #
ECHO ##################################################################
ECHO.
ECHO ESTE SCRIPT REALIZARA LAS SIGUIENTES ACCIONES:
ECHO   1. Detendra y eliminara todos los contenedores de Docker.
ECHO   2. BORRARA PERMANENTEMENTE el volumen de la base de datos (postgres_data).
ECHO   3. Reconstruira la imagen del bot desde cero.
ECHO   4. Levantara todos los servicios en segundo plano.
ECHO   5. Ejecutara todas las migraciones de la base de datos.
ECHO.

PAUSE

ECHO.
ECHO --- PASO 1 de 4: Deteniendo contenedores y eliminando volumen... ---
docker-compose down -v
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error deteniendo los contenedores. Abortando.
    EXIT /B 1
)

ECHO.
ECHO --- PASO 2 de 4: Reconstruyendo y levantando servicios... ---
docker-compose up --build -d
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error levantando los contenedores. Abortando.
    EXIT /B 1
)

ECHO.
ECHO --- PASO 3 de 4: Esperando a que la base de datos se inicie (5 segundos)... ---
timeout /t 5 /nobreak > NUL

ECHO.
ECHO --- PASO 4 de 4: Ejecutando migraciones de la base de datos... ---
docker-compose run --rm bot alembic upgrade head
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error ejecutando las migraciones. Revisa los logs.
    EXIT /B 1
)

ECHO.
ECHO ##################################################################
ECHO #                ¡PROCESO COMPLETADO CON EXITO!                  #
ECHO ##################################################################
ECHO.