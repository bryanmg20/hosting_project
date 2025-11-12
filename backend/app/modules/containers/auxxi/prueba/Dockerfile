# Usamos una imagen base de Node.js para la construcción de la app
FROM node:18-alpine as build

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de package.json y package-lock.json
COPY package*.json ./

# Instala las dependencias del proyecto
RUN npm install

# Copia el código fuente del proyecto
COPY . .

# Construye la aplicación para producción (en caso de ser una aplicación React o cualquier SPA)
RUN npm run build

# Segunda etapa: solo copiamos los archivos estáticos construidos
FROM alpine:latest

# Directorio donde serviremos los archivos estáticos
WORKDIR /usr/share/app

# Copia los archivos estáticos construidos desde la etapa de construcción
COPY --from=build /app/build /usr/share/app

# Exponemos el puerto 8080
EXPOSE 8080

# No necesitamos un servidor HTTP, solo los archivos estáticos
CMD ["echo", "Contenedor listo, sirviendo archivos estáticos."]
