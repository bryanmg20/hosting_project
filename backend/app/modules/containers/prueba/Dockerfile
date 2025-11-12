# Usa una imagen base de Node.js
FROM node:20-alpine AS build

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo package.json y package-lock.json (si existe)
COPY package*.json ./

# Instala las dependencias
RUN npm install

# Copia el código fuente
COPY . .

# Construye la aplicación para producción
RUN npm run build

# Usa una imagen base de Nginx para servir la aplicación
FROM nginx:alpine

# Copia los archivos de la build al directorio de Nginx
COPY --from=build /app/build /usr/share/nginx/html

# Expone el puerto 80 para el contenedor
EXPOSE 80

# Comando por defecto para ejecutar el contenedor
CMD ["nginx", "-g", "daemon off;"]