# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Paper Trail is a document management app: a FastAPI backend (`backend/`) and a
React + TypeScript frontend (`frontend/`), with PDF upload, chunking, embeddings
(via Ollama), and semantic search/chat over document content stored in Postgres+pgvector.

## Commands

### Backend (`backend/`)

```bash
uv sync                # install deps
./doit.sh db-up         # start Postgres+pgvector via podman-compose (localhost:5443)
./doit.sh db-down       # stop it
./doit.sh run           # dev server with reload, http://localhost:8000/api
./doit.sh test          # run all tests (needs db-up; uses paper_trail_test db)
./doit.sh lint          # ruff check
./doit.sh lint-fix      # ruff check --fix + ruff format
```

Set `CONTAINER_ENGINE=docker` to use Docker instead of Podman (default).

Run a single test:

```bash
uv run pytest tests/routes/test_documents.py::test_create_document -v
```

Generate JWTs for manual testing:

```bash
uv run scripts/generate_token.py         # user token
uv run scripts/generate_token.py admin   # admin token
```

### Frontend (`frontend/`)

```bash
bun dev       # Vite dev server
bun run build # tsc -b && vite build
bun run lint  # oxlint
```

### Combined image

`backend/Dockerfile` builds the frontend with Bun, copies `frontend/dist` into the
image as `backend/static`, and serves both from one origin on port `8040`. Because it
needs both `backend/` and `frontend/`, **the build context is the repo root**, not
`backend/` — use `./doit.sh docker-build` / `./doit.sh docker-run` from `backend/`
rather than running `podman build`/`docker build` directly.

## Architecture

### Same-origin split between dev and prod

In dev, Vite (`frontend/`, port 5173 by default) and FastAPI (`backend/`, port 8000)
run as separate origins; the frontend talks to the API cross-origin via `VITE_API_URL`
(`frontend/src/lib/api.ts` defaults to `/api`), and CORS is controlled by `CORS_ORIGINS`
in `backend/app/config.py`. In the combined Docker image there is no dev server —
`backend/app/main.py` mounts the built frontend as static files and serves
`index.html` for any non-`/api` path (SPA client-side routing), so the two modes must
stay consistent: **all API routes live under `/api`** specifically so they never
collide with SPA routes on the same origin.

### Backend: four-schema model pattern

Every resource in `backend/app/models/` follows: `Model` (table=True), `ModelCreate`
(request validation), `ModelUpdate` (partial update, every field `Optional`), and
`ModelRead` (response shape). PATCH routes use `model.model_dump(exclude_unset=True)`
so unset fields don't overwrite existing data. `updated_at` is not a DB trigger —
every PUT/PATCH route must set `db_obj.updated_at = datetime.now(UTC)` explicitly
before commit. Tables are created via `SQLModel.metadata.create_all` in the `lifespan`
hook in `main.py` (no migrations yet — see doc comment there before adding one).

New resources: add the model, add a route file protected with
`Depends(require_user)` / `Depends(require_admin)`, then register the router in
`app/main.py`.

### Document ingestion pipeline

`POST /api/documents/upload` (`backend/app/routes/documents.py`) is the core flow:
save the raw PDF to `RAW_PDF_DIR`, extract markdown via `app/pdf.py`
(`pymupdf4llm`), split it into overlapping chunks via `app/chunking.py`
(paragraph-boundary aware), embed each chunk via `app/embeddings.py`, and store one
`DocumentChunk` row per chunk. `Document.embedding` is a *separate*, single vector
that only embeds the document's `name` (used by `GET /documents/search`) — it is
not what chat retrieval searches. Chat (`app/routes/chat.py`, `app/chat.py`) embeds
the question, finds the nearest `DocumentChunk` rows by cosine distance, and asks
`ChatOllama` a question grounded only in that retrieved context.

Both embeddings and chat go through Ollama (`OLLAMA_BASE_URL`, host machine, not in
compose) — `EMBEDDING_MODEL`/`EMBEDDING_DIM` and `CHAT_MODEL` in `.env` must match
what's pulled locally. The `Vector` column dimension (`document.py`,
`document_chunk.py`) must exactly match `EMBEDDING_DIM`; changing embedding models
requires updating both and recreating the tables.

### Auth

RS256 JWT, no session/cookie state. `app/auth/jwt.py` decodes the bearer token
against `JWT_PUBLIC_KEY`; `app/auth/permissions.py` provides `require_user` (any
valid token) and `require_admin` (role claim must be `"admin"`) as route
dependencies — there's no per-route inline role checking. JWT payload fields should
be accessed with `.get()`, not direct indexing, since claims aren't guaranteed.
Frontend (`frontend/src/lib/api.ts`) stores the token in `localStorage` and decodes
the payload client-side only for display (`getCurrentUser`) — not a signature check.
See `backend/docs/authentication-architecture.md` for more detail.

### Async DB testing

Tests run against a real Postgres (`paper_trail_test`, a separate database on the
same compose Postgres instance — never mocked), not sqlite/in-memory. The `client`
fixture in `backend/tests/conftest.py` is an `httpx.AsyncClient` over
`ASGITransport`, not a sync `TestClient` — asyncpg connections are bound to the
event loop that opened them, and a sync client's separate thread/loop breaks against
real Postgres. `tests/routes/test_document_embeddings.py` monkeypatches
`app.embeddings.embed_text` so most tests don't need a live Ollama instance.

### Frontend routing and layout

TanStack Router with file-based routes in `frontend/src/routes/`; `routeTree.gen.ts`
is generated — never edit it by hand. Layout routes use the `_app` prefix
(`_app.tsx` is the shared sidebar/header shell, `_app.index.tsx`,
`_app.admin.documents.tsx`, `_app.admin.users.tsx` render inside its `Outlet`).
`src/components/ui/` is reserved for shadcn-generated primitives only; app-specific
components go in `src/components/layout/` or `src/components/` directly.

## Context Files
Read the following to get the full context of the project:

@context/project-overview.md
@context/coding-standards.md
@context/ai-interaction.md
@context/testing-instructions.md
@context/current-feature.md
