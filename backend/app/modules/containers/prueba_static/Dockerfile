# Imagen base de Node.js
FROM node:18-alpine

# Instalamos http-server para servir contenido estático
RUN npm install -g http-server

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del sitio estático
COPY ./public/ /app/public/

# Exponemos el puerto correcto (debe coincidir con el CMD)
EXPOSE 80

# Usuario no root (opcional, pero buena práctica)
RUN addgroup -g 1001 -S app && adduser -u 1001 -S app -G app
USER app

# Comando para lanzar el servidor HTTP
CMD ["http-server", "public", "-p", "80", "--cors", "-a", "0.0.0.0"]