_# Etapa de construcción
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código fuente
COPY . .

# Etapa de producción
FROM node:20-alpine AS production

WORKDIR /app

# Copiar solo los archivos necesarios de la etapa de construcción
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/src ./src
COPY --from=builder /app/utils ./utils
COPY --from=builder /app/package.json ./package.json

# Exponer el puerto
EXPOSE 3000

# Comando de inicio
CMD ["node", "src/index.js"]_
