# Paper Trail API

FastAPI backend for Paper Trail — async SQLAlchemy/SQLModel, Postgres + pgvector,
RS256 JWT auth with role-based permissions, and structured logging.

## Quick Start

### Prerequisites

- Python 3.11+
- Podman + podman-compose (runs Postgres with the pgvector extension)
- [uv](https://docs.astral.sh/uv/) for dependency management
- [Ollama](https://ollama.com) running locally with `qwen3-embedding:4b` pulled
  (`ollama pull qwen3-embedding:4b`) — Ollama runs on the host, not in compose

### Installation

```bash
uv sync
cp .env.example .env
# edit .env with your configuration
./doit.sh db-up   # starts Postgres+pgvector on localhost:5443
```

Generate RSA keys for JWT (if not provided):

```bash
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -pubout -out public_key.pem
# add to .env (replace newlines with \n)
```

Run the dev server:

```bash
./doit.sh run
# or: uv run uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000/api` (`/docs` for Swagger UI, `/redoc`
for ReDoc). In dev, the frontend runs separately via Vite (`bun dev` in `frontend/`)
and talks to the API cross-origin — see `CORS_ORIGINS` below. The combined Docker
image serves both from one origin instead (see "Combined image" below).

## Development Commands

```bash
./doit.sh run          # dev server with hot reload, http://localhost:8000/api
./doit.sh db-up        # start Postgres+pgvector via podman-compose
./doit.sh db-down      # stop the database
./doit.sh test         # run all tests (needs db-up)
./doit.sh lint         # lint
./doit.sh lint-fix     # auto-fix + format
./doit.sh docker-build # build the combined frontend+backend image (podman by default)
./doit.sh docker-run   # run it on http://localhost:8040
```

Set `CONTAINER_ENGINE=docker` to use Docker instead of Podman.

## Combined image (frontend + backend, one container)

`Dockerfile` is a 3-stage build: it builds `../frontend` with Bun, resolves backend
deps with `uv`, then copies the frontend's `dist/` into the final image as `./static`.
`app/main.py` serves it same-origin: SPA routes (e.g. `/admin/documents`) fall through
to `static/index.html` for client-side routing, while `/api/*` stays the API. Because
it needs both `backend/` and `frontend/`, **the build context is the repo root**, not
`backend/` — `./doit.sh docker-build` handles that (`cd ..` + `-f backend/Dockerfile`).
The container listens on `8040` (chosen to avoid clashing with anything already on
`8000`); `./doit.sh docker-run` maps `8040:8040`.

## Database (Postgres + pgvector)

`compose.yaml` runs `pgvector/pgvector:pg16` on `localhost:5443` (moved off 5432 to
avoid clashing with a locally installed Postgres). `db/init/` holds scripts that run
once, on first volume creation:

- `01-extensions.sql` — enables the `vector` extension on the `paper_trail` database
- `02-test-db.sql` — creates a separate `paper_trail_test` database (also with the
  `vector` extension) so the test suite never touches dev data

Table creation is handled by a `lifespan` hook in `app/main.py` that runs
`SQLModel.metadata.create_all` on startup — swap it for Alembic migrations once the
schema needs to evolve carefully in production.

## Embeddings (Ollama + pgvector)

`Document.embedding` is a `pgvector` `Vector(2560)` column, sized for
[`qwen3-embedding:4b`](https://ollama.com/library/qwen3-embedding) (2560 dimensions).
`app/embeddings.py` wraps `langchain_ollama.OllamaEmbeddings` pointed at
`OLLAMA_BASE_URL` (defaults to `http://localhost:11434`).

```bash
# store an embedding for a document's name
curl -X POST -H "Authorization: Bearer <token>" http://localhost:8000/api/documents/1/embed

# semantic search, ranked by cosine distance
curl -G -H "Authorization: Bearer <token>" \
  --data-urlencode "q=rental agreement" \
  http://localhost:8000/api/documents/search
```

If you switch embedding models, update `EMBEDDING_MODEL` and `EMBEDDING_DIM` in
`.env` to match — the column dimension must match the model's output size exactly.

## Project Structure

```
backend/
├── app/
│   ├── main.py              # application entry point + startup table creation
│   ├── config.py            # configuration & environment variables
│   ├── logger.py            # structured logging setup
│   ├── database.py          # async database connection & session
│   ├── embeddings.py        # langchain_ollama.OllamaEmbeddings wrapper
│   ├── routes/               # API endpoints (modular)
│   │   ├── root.py
│   │   ├── health.py
│   │   ├── documents.py     # CRUD + embed/search example
│   │   └── users.py         # admin-only user management
│   ├── auth/                 # authentication & authorization
│   │   ├── jwt.py
│   │   └── permissions.py
│   └── models/
│       ├── document.py      # CRUD schemas + pgvector column
│       └── user.py          # CRUD schemas
├── db/
│   └── init/                 # Postgres init scripts (run once, on first volume creation)
├── tests/
│   ├── conftest.py           # shared fixtures & test config
│   └── routes/
├── scripts/
│   └── generate_token.py     # generate JWT tokens for testing
├── docs/
│   └── authentication-architecture.md
├── compose.yaml               # Postgres + pgvector (podman-compose)
├── pyproject.toml
├── Dockerfile
└── doit.sh
```

## Authentication

RS256 JWT with role-based access control.

```bash
uv run scripts/generate_token.py         # user token
uv run scripts/generate_token.py admin   # admin token

curl -H "Authorization: Bearer <token>" http://localhost:8000/documents
```

See [docs/authentication-architecture.md](docs/authentication-architecture.md) for details.

## Database Models

Each resource follows a four-schema pattern:

```python
class Document(SQLModel, table=True):      # table model
class DocumentCreate(SQLModel):            # request validation (create)
class DocumentUpdate(SQLModel):            # partial update — every field Optional
class DocumentRead(SQLModel):              # response model
```

Every table model has `created_at` and `updated_at` (`DateTime(timezone=True)`,
`nullable=False`). `updated_at` isn't a DB trigger — every PUT/PATCH route sets
`db_obj.updated_at = datetime.now(UTC)` explicitly before committing.

## Extending the API

1. Add a model in `app/models/<name>.py` following the four-schema pattern above.
2. Add a route file in `app/routes/<name>.py`, protecting mutating/private routes with
   `Depends(require_user)` or `Depends(require_admin)`.
3. Register the router in `app/main.py`.

## Testing

```bash
./doit.sh db-up   # tests run against the real paper_trail_test database
uv run pytest tests/ -v
```

`tests/conftest.py` connects to `paper_trail_test` (a separate database on the same
podman-compose Postgres instance — see `db/init/02-test-db.sql`), creates/drops tables
per test, and exposes a `client` fixture (an `httpx.AsyncClient` over `ASGITransport`)
with the DB dependency overridden, plus `auth_headers` / `admin_headers` fixtures for
signed JWTs.

`client` is async because asyncpg connections are bound to the event loop that opened
them — a sync `TestClient` runs requests on a separate thread/loop and breaks against
real Postgres. `tests/routes/test_document_embeddings.py` monkeypatches
`app.embeddings.embed_text` with a fixed-dimension stand-in vector so tests don't need
a live Ollama instance.
