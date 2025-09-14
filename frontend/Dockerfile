# Imagem base
FROM node:20-alpine

WORKDIR /app

# Copiar package.json + package-lock.json
COPY package.json package-lock.json ./

# Instalar dependências
RUN npm install

# Copiar restante do código
COPY . .

# Expõe porta do React
EXPOSE 3000

# Comando para desenvolvimento com hot reload
CMD ["npm", "start"]
