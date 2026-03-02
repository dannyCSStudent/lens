FROM node:20-alpine

WORKDIR /app

COPY package.json pnpm-lock.yaml turbo.json ./
COPY apps ./apps
COPY packages ./packages

RUN npm install -g pnpm
RUN pnpm install

EXPOSE 3000
