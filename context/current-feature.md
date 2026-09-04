# Current Feature: User Dashboard

<!-- context/features/03-user-dashboard.md -->

## Status

<!-- Not Started|In Progress|Complete -->

In Progress

## Goals

- Replace the placeholder in `frontend/src/routes/_app.index.tsx` with a list
  of the current user's documents, fetched via `documentsApi.list()` and
  rendered with the existing `DataTable` pattern from
  `_app.admin.documents.tsx`.
- Each row is selectable (button or row click) to become the "active"
  document — this selection is the hook the document-chat feature
  (`04-document-chat.md`) will build on. Track it as local component state
  (e.g. `useState<Document | null>`); it does not need to persist or sync
  with the URL.
- Keep the route's file path and exported `Route` (`/_app/`) unchanged — only
  the `Index`/component body changes.
- No backend changes.

## Notes

- Depends on: none.
- Use TanStack Query (`useQuery`) for `documentsApi.list()`, per
  `context/coding-standards.md` — server state does not belong in local
  state/Zustand/Redux.
- This spec intentionally stops at "selection exists as state" — it does not
  render a chat panel. `04-document-chat.md` depends on this and wires the
  panel in.
- No Zod schema needed here (no form submission on this page).
- Testing: manual — log in as a regular user, confirm `/` shows the document
  list instead of the placeholder, and confirm rows are selectable. No
  backend tests needed (no backend changes).

## History

<!-- Keep this updated. Earliest to latest -->

- **Document Upload UI** (`context/features/02-document-upload-ui.md`) — merged 2026-09-04
  (92c7aa0). Added a separate "Upload PDF" dialog to
  `frontend/src/routes/_app.admin.documents.tsx` (file, name, description, source, tags — no
  doctype/status), wired via `uploadMutation` to `documentsApi.upload` following the existing
  `createMutation` convention. No backend changes.
