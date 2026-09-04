# Build context is the repo root (see doit.sh docker-build) since this image
# combines the frontend build output with the backend.

# Stage 1: build the frontend (bun)
FROM docker.io/oven/bun:1 AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/bun.lock ./
RUN bun install --frozen-lockfile
COPY frontend/ ./
RUN bun run build

# Stage 2: resolve backend dependencies (uv)
FROM python:3.11-slim AS backend-builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Stage 3: production image
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 appuser
WORKDIR /app

# Copy virtual environment from builder
COPY --from=backend-builder /app/.venv /app/.venv

# Copy application code
COPY backend/app/ ./app/

# Copy the built frontend; app/main.py serves it from ./static when present
COPY --from=frontend-builder /frontend/dist ./static

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add virtual environment to PATH
ENV PATH=/app/.venv/bin:$PATH

# Pre-compile Python files for faster startup
RUN python -m compileall app/

# Expose port
EXPOSE 8040

# Run with Gunicorn + Uvicorn workers
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8040", \
     "--timeout", "30"]
