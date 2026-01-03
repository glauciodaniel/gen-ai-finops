# frontend/Dockerfile

# Estágio 1: Build (Gera os arquivos estáticos)
FROM node:20-alpine as builder

WORKDIR /app

# Instala dependências
COPY package*.json ./
COPY package-lock.json* ./
RUN npm ci

# Copia código fonte e faz o build
COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig*.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY postcss.config.js* ./
COPY eslint.config.js ./
COPY src/ ./src/
RUN npm run build

# Estágio 2: Produção (Servidor Nginx leve)
FROM nginx:alpine

# Copia a configuração customizada do Nginx (veja passo 3)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia os arquivos gerados no estágio anterior para o Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

