## Project Specifications

Paper Trail is a document management app: a FastAPI backend and a React +
TypeScript frontend, with PDF upload, parsing, semantic search, and chat over
document content, backed by Postgres + pgvector and local Ollama models.

---

## Problem (Core Idea)

Give users a place to store documents (PDFs and, longer-term, other doctypes),
automatically extract and index their content, and let users find and ask
questions about them by meaning rather than exact keyword — without depending on
a hosted embeddings/LLM API.

---

## Users

- **Users** — can create, view, update, upload, embed, search, and chat over
  documents.
- **Admins** — everything a user can do, plus deleting documents and managing
  user accounts (`app/routes/users.py`).

---

## ✨ Core Features

- **Document CRUD** — `backend/app/routes/documents.py`: list/get/create/update
  (PUT + PATCH)/delete, delete restricted to admins.
- **PDF upload & ingestion pipeline** — `POST /documents/upload`: saves the raw
  PDF, extracts markdown (`app/pdf.py`, `pymupdf4llm`), splits it into
  overlapping chunks on paragraph boundaries (`app/chunking.py`), embeds each
  chunk via Ollama (`app/embeddings.py`, model `qwen3-embedding:4b`), and stores
  one `DocumentChunk` row per chunk. Status moves to `pending` once processing
  completes.
- **Per-document semantic search** — `GET /documents/search`: embeds the query
  and ranks documents by cosine distance on `Document.embedding` (a
  single vector embedding the document's *name*, populated via
  `POST /documents/{id}/embed` — separate from the chunk embeddings above).
  **Not yet wired into the frontend UI.**
- **RAG chat over a document** — `POST /documents/{id}/chat`
  (`app/routes/chat.py`, `app/chat.py`): embeds the question, retrieves the
  nearest `DocumentChunk` rows for that document by cosine distance, and asks
  `ChatOllama` a question grounded only in that retrieved context.
- **User management** — admin-only CRUD over `User` records and roles.
- **Auth** — RS256 JWT via `app/auth/jwt.py` (`require_user`/`require_admin` in
  `app/auth/permissions.py`); see `backend/docs/authentication-architecture.md`.

---

## Data Model

SQLModel, async SQLAlchemy, Postgres + pgvector. Each resource follows a
four-schema pattern (table model / `*Create` / `*Update` / `*Read`) — see
`CLAUDE.md` for details.

- **`Document`** (`app/models/document.py`) — `name`, `description`, `doctype`,
  `document_source`, `tags` (Postgres array), `raw_path`/`markdown_path`
  (filesystem paths under `STORAGE_ROOT`), `status` (`draft`/`pending`/
  `approved`), `created_at`/`updated_at`, `embedding` (`Vector(EMBEDDING_DIM)`,
  name-only embedding).
- **`DocumentChunk`** (`app/models/document_chunk.py`) — `document_id` (FK),
  `chunk_index`, `content`, `embedding` (`Vector(EMBEDDING_DIM)`), `created_at`.
  One row per chunk of a document's extracted markdown; this is what chat
  retrieval searches.
- **`User`** (`app/models/user.py`) — `email`, `name`, `role`
  (`user`/`admin`), `created_at`/`updated_at`.

---

## Tech Stack

**Backend** (`backend/`): FastAPI, SQLModel + SQLAlchemy (async), asyncpg,
Postgres 16 + pgvector (via podman-compose, `localhost:5443`), RS256 JWT
(PyJWT), structlog, `langchain-ollama` (embeddings + chat against a local
Ollama instance), `pymupdf4llm` (PDF → markdown), `uv` for dependency
management, `ruff` for lint/format, `pytest` + `pytest-asyncio` + `httpx` for
tests.

**Frontend** (`frontend/`): React 19, TypeScript, Vite, TanStack Router
(file-based routes) + TanStack Query + TanStack Table, shadcn components on
`@base-ui/react`, Tailwind CSS v4, `next-themes`, `sonner` (toasts), Bun as
package manager/dev runner, `oxlint` for linting.

**Combined deployment**: `backend/Dockerfile` (3-stage) builds the frontend
with Bun and serves it same-origin from FastAPI (`app/main.py` mounts the built
`static/` dir and falls through to `index.html` for SPA routes; API stays under
`/api`). Built and run via `./doit.sh docker-build` / `./doit.sh docker-run`
(port `8040`).
