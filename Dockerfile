# syntax=docker/dockerfile:1

# ---- Stage 1: build the React/Vite frontend ----
FROM node:20-slim AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.ts vitest.config.ts tsconfig.json tsconfig.app.json tsconfig.node.json ./
COPY src ./src
COPY public ./public
RUN npm run build          # → /app/dist

# ---- Stage 2: Python backend that also serves the built frontend ----
FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
# git + ca-certificates are needed at runtime to clone public GitHub repos
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install -r backend/requirements.txt
COPY backend ./backend
COPY --from=frontend /app/dist ./dist
# Hosted defaults: never scan the container's local filesystem.
ENV AEGIS_ALLOW_FOLDER=false GOOGLE_GENAI_USE_VERTEXAI=false
WORKDIR /app/backend
# Cloud Run injects $PORT (default 8080 locally).
CMD ["sh", "-c", "exec uvicorn server:app --host 0.0.0.0 --port ${PORT:-8080}"]
