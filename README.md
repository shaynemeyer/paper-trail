# Paper Trail

A document management app: upload PDFs, extract and chunk their content, embed
it locally via Ollama, and search or chat over it by meaning rather than exact
keyword — backed by Postgres + pgvector, with no dependency on a hosted
embeddings/LLM API.

- **Backend** (`backend/`) — FastAPI, SQLModel/SQLAlchemy (async), Postgres +
  pgvector, RS256 JWT auth. See [`backend/readme.md`](backend/readme.md).
- **Frontend** (`frontend/`) — React 19, TypeScript, Vite, TanStack Router +
  Query, shadcn/Tailwind CSS v4. See [`frontend/README.md`](frontend/README.md).

## Quick start

```bash
# Backend
cd backend
uv sync
cp .env.example .env   # edit with your config (JWT keys, Ollama, etc.)
./doit.sh db-up        # Postgres + pgvector via podman-compose, localhost:5443
./doit.sh run          # dev server, http://localhost:8000/api

# Frontend (separate terminal)
cd frontend
bun install
bun dev                # Vite dev server, talks to the API cross-origin
```

Requires [Ollama](https://ollama.com) running locally with the configured
embedding/chat models pulled (see `backend/.env` for `EMBEDDING_MODEL` /
`CHAT_MODEL`) — Ollama runs on the host, not in the compose stack.

## Combined image

`backend/Dockerfile` builds the frontend with Bun and serves both frontend and
API from one FastAPI origin on port `8040`. Build context is the repo root:

```bash
cd backend
./doit.sh docker-build
./doit.sh docker-run
```

## Core features

- **PDF upload & ingestion** — upload a PDF, extract markdown, split into
  overlapping chunks, embed each chunk via Ollama, store per-chunk vectors.
- **Semantic search** — rank documents by cosine distance on a name-level
  embedding.
- **RAG chat over a document** — ask questions grounded only in that
  document's retrieved chunks.
- **User management** — admin-only CRUD over users and roles.
- **Auth** — RS256 JWT, role-based route guards (`user` / `admin`).

## Documentation

- [`CLAUDE.md`](CLAUDE.md) — architecture notes and conventions for AI-assisted
  development in this repo.
- [`context/project-overview.md`](context/project-overview.md) — full feature
  and data model spec.
- [`context/coding-standards.md`](context/coding-standards.md) — backend and
  frontend code conventions.
- [`backend/docs/authentication-architecture.md`](backend/docs/authentication-architecture.md)
  — JWT auth design.
- [`context/features/`](context/features/) — individual feature specs, tracked
  via the `/feature` workflow (see [`context/ai-interaction.md`](context/ai-interaction.md)).
