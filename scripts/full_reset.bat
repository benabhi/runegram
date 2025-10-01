@ECHO OFF
REM ##################################################################
REM #                                                                #
REM #           SCRIPT DE REINICIO COMPLETO PARA RUNEGRAM              #
REM #                                                                #
REM #  Este script automatiza el proceso de limpiar por completo el  #
REM #  entorno de desarrollo de Docker y reconstruirlo desde cero.   #
REM #                                                                #
REM #  Es la herramienta principal para asegurar un estado limpio    #
REM #  después de cambios en dependencias, migraciones o si algo     #
REM #  se ha corrompido.                                             #
REM #                                                                #
REM ##################################################################

TITLE Reinicio Completo de Runegram

CLS
ECHO.
ECHO  ##################################################################
ECHO  #            SCRIPT DE REINICIO COMPLETO PARA RUNEGRAM           #
ECHO  ##################################################################
ECHO.
ECHO  ESTE SCRIPT REALIZARA LAS SIGUIENTES ACCIONES DE FORMA DESTRUCTIVA:
ECHO.
ECHO    1. Detendra todos los contenedores de la aplicacion.
ECHO    2. Eliminara los contenedores detenidos.
ECHO    3. [!] Eliminara el VOLUMEN de la base de datos, borrando TODOS los datos.
ECHO    4. Reconstruira la imagen Docker de la aplicacion desde cero.
ECHO    5. Levantara todos los servicios en segundo plano.
ECHO.
ECHO  Las migraciones se ejecutaran automaticamente al iniciar el bot.
ECHO.
ECHO  Presiona cualquier tecla para continuar o cierra esta ventana para cancelar.
PAUSE

ECHO.
ECHO --- PASO 1 de 2: Deteniendo contenedores y eliminando volumen de datos... ---
ECHO.
REM `docker-compose down` detiene y elimina los contenedores.
REM La bandera `-v` (o `--volumes`) es crucial, ya que elimina los volúmenes
REM nombrados asociados, como `postgres_data`, asegurando un borrado total.
docker-compose down -v

ECHO.
ECHO --- PASO 2 de 2: Reconstruyendo la imagen y levantando servicios... ---
ECHO.
REM `docker-compose up` levanta los servicios.
REM La bandera `--build` fuerza la reconstrucción de la imagen 'bot' desde el Dockerfile.
REM La bandera `-d` (o `--detach`) ejecuta los contenedores en segundo plano.
docker-compose up --build -d

ECHO.
ECHO  ##################################################################
ECHO  #                ¡PROCESO COMPLETADO CON EXITO!                  #
ECHO  #----------------------------------------------------------------#
ECHO  #  Los contenedores estan corriendo en segundo plano.            #
ECHO  #  Puedes ver los logs con: docker-compose logs -f bot            #
ECHO  ##################################################################
ECHO.