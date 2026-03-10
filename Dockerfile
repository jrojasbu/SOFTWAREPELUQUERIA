# Usar la imagen oficial liviana de Python.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Permitir que los mensajes de log aparezcan inmediatamente en los registros de Knative
ENV PYTHONUNBUFFERED True

# Configurar el directorio de trabajo
ENV APP_HOME /app
WORKDIR $APP_HOME

# Instalar dependencias de sistema necesarias para xhtml2pdf y procesamiento de imágenes (Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \    
    gcc \
    libcairo2 \
    libcairo2-dev \
    pkg-config \   
    libpangocairo-1.0-0 \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de dependencias e instalarlas
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código local a la imagen del contenedor
COPY . ./

# Puerto expuesto por defecto para documentación (Cloud Run inyectará el valor real en $PORT)
EXPOSE 8080

# Ejecutar el servicio web al iniciar el contenedor. Usamos gunicorn
# con un proceso worker y 8 hilos.
# Para entornos con múltiples núcleos, se puede aumentar el número de workers.
# Timeout se pone en 0 para dejar que Cloud Run maneje el escalado de instancias.
CMD exec gunicorn --bind :${PORT:-8080} --workers 1 --threads 8 --timeout 0 app:app
