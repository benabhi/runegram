#!/bin/sh

# Salimos inmediatamente si un comando falla
set -e

echo "--- Esperando a que PostgreSQL esté disponible... ---"
# El host 'postgres' es el nombre del servicio en docker-compose.yml
# Bucle hasta que el puerto 5432 de postgres esté abierto
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "--- PostgreSQL está listo. ---"

echo "--- Ejecutando migraciones de la base de datos... ---"
alembic upgrade head

echo "--- ¡Migraciones completadas! Iniciando el bot... ---"
# 'exec "$@"' ejecuta el comando que se le pasa al script.
# En nuestro caso, será 'python run.py'
exec "$@"