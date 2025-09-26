@ECHO OFF
CLS
ECHO.
ECHO ##################################################################
ECHO #            SCRIPT DE REINICIO COMPLETO PARA RUNEGRAM           #
ECHO ##################################################################
ECHO.
ECHO ESTE SCRIPT REALIZARA LAS SIGUIENTES ACCIONES:
ECHO   1. Detendra y eliminara todos los contenedores y el volumen de la BD.
ECHO   2. Reconstruira la imagen del bot y levantara todos los servicios.
ECHO.
ECHO Las migraciones se ejecutaran automaticamente al iniciar el bot.
ECHO.

PAUSE

ECHO.
ECHO --- PASO 1 de 2: Deteniendo contenedores y eliminando volumen... ---
docker-compose down -v

ECHO.
ECHO --- PASO 2 de 2: Reconstruyendo y levantando servicios... ---
docker-compose up --build -d

ECHO.
ECHO ##################################################################
ECHO #                ¡PROCESO COMPLETADO CON EXITO!                  #
ECHO ##################################################################
ECHO.