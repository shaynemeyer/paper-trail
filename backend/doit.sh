#!/bin/bash

# Container engine: defaults to podman, override with CONTAINER_ENGINE=docker
CONTAINER_ENGINE="${CONTAINER_ENGINE:-podman}"

case "$1" in
  run)
    uv run uvicorn app.main:app --reload
    ;;
  db-up)
    podman-compose up -d
    ;;
  db-down)
    podman-compose down
    ;;
  test)
    uv run pytest tests/ -v
    ;;
  lint)
    uv run ruff check app/ tests/
    ;;
  lint-fix)
    uv run ruff check --fix app/ tests/
    uv run ruff format app/ tests/
    ;;
  docker-build)
    # Context is the repo root: the image combines this backend with ../frontend
    (cd .. && "$CONTAINER_ENGINE" build -f backend/Dockerfile -t paper-trail:latest .)
    ;;
  docker-run)
    "$CONTAINER_ENGINE" run -p 8040:8040 --env-file .env paper-trail:latest
    ;;
  *)
    echo "Usage: ./doit.sh {run|db-up|db-down|test|lint|lint-fix|docker-build|docker-run}"
    echo "Set CONTAINER_ENGINE=docker to use Docker instead of Podman."
    exit 1
    ;;
esac
