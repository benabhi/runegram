#!/bin/sh
#
# Entrypoint para el Contenedor de la Aplicación Runegram
#
# Este script se ejecuta cada vez que el contenedor de la aplicación ('bot') se inicia.
# Su principal responsabilidad es preparar el entorno antes de lanzar la aplicación
# de Python principal.
#
# Tareas:
# 1. Esperar a que el servicio de PostgreSQL esté completamente disponible y acepte conexiones.
#    Esto evita que la aplicación falle al arrancar si el contenedor de la base de datos
#    tarda más en iniciarse.
# 2. Ejecutar las migraciones de la base de datos con Alembic para asegurar que el
#    esquema de la base de datos esté actualizado con la última versión del código.
# 3. Ejecutar el comando principal del contenedor (CMD), que en nuestro caso es
#    `python run.py`, para iniciar el bot.
#
# `set -e`: Este comando es crucial. Asegura que el script se detenga inmediatamente
# si cualquier comando falla (devuelve un código de salida distinto de cero).
#
set -e

# --- PASO 1: Esperar a PostgreSQL ---
echo "--- [Entrypoint] Esperando a que PostgreSQL esté disponible... ---"
# El host 'postgres' es el nombre del servicio definido en docker-compose.yml.
# El comando `nc -z` (netcat) intenta establecer una conexión sin enviar datos.
# El bucle `while` se repetirá hasta que el puerto 5432 de 'postgres' esté abierto.
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "--- [Entrypoint] ✅ PostgreSQL está listo. ---"


# --- PASO 2: Ejecutar Migraciones de la Base de Datos ---
echo "--- [Entrypoint] Ejecutando migraciones de la base de datos con Alembic... ---"
# `alembic upgrade head` aplica todas las migraciones pendientes desde la última
# versión registrada en la base de datos hasta la última versión en los archivos.
alembic upgrade head
echo "--- [Entrypoint] ✅ Migraciones completadas. ---"


# --- PASO 3: Ejecutar el Comando Principal ---
echo "--- [Entrypoint] Iniciando la aplicación principal del bot... ---"
# `exec "$@"` es una construcción de shell especial.
# 'exec' reemplaza el proceso actual del script con el nuevo comando, lo que es
# más eficiente y permite que las señales del sistema (como un 'docker stop')
# lleguen directamente a la aplicación de Python.
# `"$@"` expande todos los argumentos que se pasaron al script. En nuestro caso,
# `docker-compose.yml` pasa `python run.py`, por lo que este comando se convierte en
# `exec python run.py`.
exec "$@"