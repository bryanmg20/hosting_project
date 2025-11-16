FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo requirements.txt
COPY requirements.txt .

# Instala las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente de la aplicación
COPY . .

# Expone el puerto 5000 para el contenedor
EXPOSE 80

# Comando para ejecutar la aplicación Flask
CMD ["python", "app.py"]
