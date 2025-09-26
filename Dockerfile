# Dockerfile
# Usamos alpine, que es muy ligero, por lo que tenemos que añadir paquetes
FROM python:3.11-alpine

# Instalamos netcat (viene en el paquete 'netcat-openbsd') y git
RUN apk add --no-cache netcat-openbsd git

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos nuestro script de entrada y nos aseguramos de que es ejecutable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

COPY . .

# El entrypoint se define en docker-compose.yml,
# el CMD es el comando que se le pasa.
CMD ["python", "run.py"]