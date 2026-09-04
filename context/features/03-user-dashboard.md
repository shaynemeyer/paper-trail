# User Dashboard

**Status:** Not Started
**Depends on:** none

## Context

Source plan: `docs/plan-user-dashboard-chat.md`, section "1. User dashboard
(`frontend/src/routes/_app.index.tsx`)".

`frontend/src/routes/_app.index.tsx` currently renders a static "Your
dashboard is coming soon" placeholder (see current content below) instead of
anything useful. It keeps the route path `/_app/` — only the component body
changes.

```tsx
import { createFileRoute } from '@tanstack/react-router'
import { ScrollText } from 'lucide-react'

export const Route = createFileRoute('/_app/')({
  component: Index,
})

function Index() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-3 text-center">
      <div className="flex size-12 items-center justify-center rounded-lg bg-accent text-accent-foreground">
        <ScrollText className="size-6" />
      </div>
      <h1 className="text-xl font-semibold">Your dashboard is coming soon</h1>
      <p className="max-w-sm text-sm text-muted-foreground">
        A personalized view of your documents will live here.
      </p>
    </div>
  )
}
```

Reference pattern to follow: the `DataTable` usage in
`frontend/src/routes/_app.admin.documents.tsx` (existing admin documents
page) — reuse the same table/list approach for consistency, backed by
`documentsApi.list()` from `frontend/src/lib/api.ts`.

`documentsApi.list()` returns `Document[]` (see `frontend/src/lib/api.ts`):

```ts
export interface Document {
  id: number
  name: string
  description: string
  doctype: string
  document_source: string | null
  status: DocumentStatus
  raw_url: string | null
  markdown_url: string | null
  created_at: string
  updated_at: string
}
```

## Goals

- Replace the placeholder in `frontend/src/routes/_app.index.tsx` with a list
  of the current user's documents, fetched via `documentsApi.list()` and
  rendered with the existing `DataTable` pattern from
  `_app.admin.documents.tsx`.
- Each row is selectable (button or row click) to become the "active"
  document — this selection is the hook the document-chat feature
  (`04-document-chat.md`) will build on. Track it as local component state
  for now (e.g. `useState<Document | null>`); it does not need to persist or
  sync with the URL.
- Keep the route's file path and exported `Route` (`/_app/`) unchanged — only
  the `Index`/component body changes.
- No backend changes.

## Notes

- Use TanStack Query (`useQuery`) for `documentsApi.list()`, per
  `context/coding-standards.md` — server state does not belong in local
  state/Zustand/Redux.
- This spec intentionally stops at "selection exists as state" — it does not
  render a chat panel. `04-document-chat.md` depends on this and wires the
  panel in.
- No Zod schema needed here (no form submission on this page).

## Testing

- Manual: log in as a regular user, confirm `/` shows the document list
  instead of the placeholder, and confirm rows are selectable.
- No backend tests needed (no backend changes).
