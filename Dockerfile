# Dockerfile para la Aplicación Runegram MUD
#
# Este archivo define los pasos para construir la imagen Docker que contendrá
# y ejecutará la aplicación del bot. Docker utiliza esta "receta" para crear un
# entorno autocontenido y reproducible.
#
# El proceso de construcción sigue estos pasos:
# 1. FROM: Se parte de una imagen base oficial de Python sobre Alpine Linux.
# 2. RUN (apk): Se instalan las dependencias a nivel de sistema operativo que
#    necesita nuestra aplicación (ej: librerías de PostgreSQL, herramientas de red).
# 3. WORKDIR: Se establece el directorio de trabajo dentro del contenedor.
# 4. COPY / RUN (pip): Se copia primero el archivo de dependencias de Python y se
#    instalan. Este paso se hace por separado para aprovechar la caché de Docker.
#    Si el `requirements.txt` no cambia, Docker no volverá a ejecutar este paso,
#    acelerando construcciones futuras.
# 5. COPY (código fuente): Se copia el resto del código de la aplicación.
# 6. CMD: Se define el comando por defecto que se ejecutará al iniciar el contenedor,
#    el cual es interceptado y gestionado por nuestro `entrypoint.sh`.

# 1. Imagen Base
# Usamos la imagen oficial de Python 3.11 basada en Alpine Linux.
# Alpine es una distribución muy ligera, lo que resulta en una imagen final más pequeña.
FROM python:3.11-alpine

# 2. Dependencias del Sistema
# Usamos el gestor de paquetes de Alpine (`apk`) para instalar software necesario.
# --no-cache: No guarda el índice de paquetes, manteniendo la imagen ligera.
# - postgresql-libs: Librerías C requeridas por el driver `psycopg2-binary`.
# - netcat-openbsd: Herramienta de red utilizada en `entrypoint.sh` para esperar a PostgreSQL.
# - git: Puede ser útil para instalar dependencias de Python directamente desde repositorios.
RUN apk add --no-cache postgresql-libs netcat-openbsd git

# 3. Directorio de Trabajo
# Establece el directorio de trabajo por defecto dentro del contenedor.
# Todos los comandos `RUN`, `CMD`, `ENTRYPOINT`, `COPY` y `ADD` posteriores
# se ejecutarán en este directorio.
WORKDIR /app

# 4. Dependencias de Python
# Copiamos solo el archivo de requerimientos primero. Esto es una optimización
# de la caché de Docker. Si nuestro código cambia pero `requirements.txt` no,
# Docker reutilizará la capa de imagen ya existente donde se instalaron las
# dependencias, haciendo que la reconstrucción sea mucho más rápida.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Código Fuente de la Aplicación
# Copiamos nuestro script de entrada y nos aseguramos de que es ejecutable.
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copiamos el resto del código fuente del proyecto al directorio de trabajo (`/app`).
COPY . .

# 6. Comando de Ejecución
# Define el comando por defecto que se ejecutará al iniciar un contenedor
# a partir de esta imagen.
# IMPORTANTE: Este comando se pasa como argumento a nuestro `entrypoint.sh`
# (definido en `docker-compose.yml`), que lo ejecuta al final con `exec "$@"`.
CMD ["python", "run.py"]