# Coding Standards

Conventions differ between the two sub-projects — documented separately rather
than forced into one shared set of rules.

## Backend (`backend/app/`)

- **Python 3.11+ union syntax**: `str | None`, `list[int]`, never
  `Optional[...]`/`List[...]`.
- **One router per resource file** in `app/routes/` (`documents.py`,
  `users.py`, `chat.py`, `health.py`, `root.py`); register each in
  `app/main.py` under the `/api` prefix.
- **Four-schema pattern per model** in `app/models/<name>.py`: `Model`
  (`table=True`), `ModelCreate` (request validation), `ModelUpdate` (partial
  update — every field `Optional`), `ModelRead` (response shape). PATCH routes
  use `model_dump(exclude_unset=True)` so unset fields don't overwrite existing
  data.
- **Timestamps**: every table model has `created_at` and `updated_at` as
  `Field(default_factory=lambda: datetime.now(UTC), sa_column=Column(DateTime(timezone=True), nullable=False))`.
  `updated_at` is not a DB trigger — every PUT/PATCH route sets
  `db_obj.updated_at = datetime.now(UTC)` explicitly before `commit()`.
- **Routes are always `async def`**; DB access is always
  `await session.execute(select(...))` / `await session.commit()` /
  `await session.refresh(...)` — never a sync call, never raw SQL strings.
- **DB session** via `Depends(get_session)` (`app/database.py`) — never
  instantiate a session manually.
- **Auth**: every non-public route takes `Depends(require_user)` or
  `Depends(require_admin)` (`app/auth/permissions.py`) — no inline role
  checks in a route body. JWT payload fields are read with `.get()`
  (`user.get("sub")`), never direct indexing.
- **Logging**: `app.logger.get_logger(__name__)`, snake_case event names
  (`"document_created"`, `"document_uploaded"`), structured kwargs including
  `user_id` on mutating routes — never `print()`.
- **Business logic that doesn't fit a one-liner stays in a helper module**
  (`app/chunking.py`, `app/pdf.py`, `app/embeddings.py`, `app/chat.py`) rather
  than inline in the route function.
- **Lint/format**: `ruff` via `./doit.sh lint` / `./doit.sh lint-fix`; rules
  live in `pyproject.toml` — refer to it rather than restating.

## Frontend (`frontend/src/`)

- **Functional components only** — no class components anywhere in the
  codebase.
- **Server state lives in TanStack Query** (`useQuery`/`useMutation`); there is
  no Zustand/Redux/other client-state store in the project — don't introduce
  one for server data.
- **Mutations follow a fixed shape**: `onSuccess` → invalidate the relevant
  query key (`queryClient.invalidateQueries({ queryKey: [...] })`) +
  `toast.success(...)` (+ close any open dialog); `onError` →
  `toast.error(err.message)`. See `_app.admin.documents.tsx` for the reference
  implementation.
- **Routing**: TanStack Router, file-based routes in `src/routes/`. Layout
  routes use the `_app` prefix (`_app.tsx` is the shared sidebar/header shell
  that other `_app.*` routes render inside via `Outlet`).
  `src/routeTree.gen.ts` is generated — never hand-edit it.
- **Components**: `src/components/ui/` is reserved for shadcn-generated
  primitives only; app-specific components go in `src/components/layout/` or
  directly under `src/components/`. If you need to create custom versions of shadcn components put them in components/{domain}/{component-name}.tsx
- **API access**: all HTTP calls go through `src/lib/api.ts` — a small
  `request<T>()` wrapper (adds the bearer token, throws a typed `ApiError`
  with the server's `detail` message on non-2xx) plus one `*Api` object per
  resource (`documentsApi`, `usersApi`). Add new endpoints there rather than
  calling `fetch` directly from a route component.
- **Forms**: currently plain `useState` + controlled inputs, submitted via a
  manual `onSubmit` handler that calls `mutation.mutate(...)` — there is no
  Zod/`react-hook-form` usage yet despite being common in this stack. Follow
  the existing plain-state pattern rather than introducing a form library
  unless asked to.
- **Styling**: Tailwind CSS v4 — configuration lives in `@theme` blocks in
  `src/index.css`, there is no `tailwind.config.ts`/`.js`. No inline `style={}`
  props.
- **Lint**: `oxlint`, config in `.oxlintrc.json` — refer to it rather than
  restating its rules.
