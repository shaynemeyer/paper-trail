# Testing Instructions

## Backend (`backend/`)

**Runner:** `pytest` + `pytest-asyncio` (`asyncio_mode = "auto"`, set in
`pyproject.toml`). Tests live in `backend/tests/routes/`.

**Run:**

```bash
./doit.sh db-up   # must be running first — tests hit a real Postgres db
./doit.sh test    # or: uv run pytest tests/ -v
```

Tests run against `paper_trail_test`, a separate database on the same
podman-compose Postgres instance (`db/init/02-test-db.sql`) — never sqlite or
an in-memory DB. Tables are created/dropped per test by the `async_session`
fixture in `tests/conftest.py`.

**Key fixtures** (`tests/conftest.py`):
- `client` — an `httpx.AsyncClient` over `ASGITransport`, **not** the sync
  `TestClient`. asyncpg connections are bound to the event loop that opened
  them; a sync client runs requests on a separate thread/loop and breaks
  against real Postgres.
- `auth_headers` / `admin_headers` — signed RS256 JWTs for a `user`/`admin`.
- `sample_documents` / `sample_users` — pre-populated rows for list/search
  tests.

**When to write a test:** one test per new route or behavior change — success
path, the relevant auth failure (401/403), and 404/422 cases already follow
this pattern in `test_documents.py`/`test_users.py`. For embedding-dependent
routes, monkeypatch `app.embeddings.embed_text` with a fixed-dimension vector
(see `test_document_embeddings.py`) rather than requiring a live Ollama
instance — reserve real Ollama calls for manual/local verification only.

**Single test:**

```bash
uv run pytest tests/routes/test_documents.py::test_create_document -v
```

**Lint (not tests, but part of the same gate):** `./doit.sh lint` /
`./doit.sh lint-fix` (ruff check + format).

## Frontend (`frontend/`)

**No test runner is configured.** `package.json` has no `test` script and no
Vitest/Jest dependency. `playwright` is listed as a devDependency but is not
wired up to any config or script — treat it as unused, not as an existing E2E
setup to extend.

Until a runner is added, frontend changes are verified manually:

```bash
bun dev          # exercise the feature in the browser
bun run lint     # oxlint
bun run build    # tsc -b && vite build — catches type errors
```

Do not invent a testing workflow (Vitest config, test files, etc.) unless
explicitly asked to add one — this file should be updated at that point.
