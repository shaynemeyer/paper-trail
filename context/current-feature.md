# Current Feature

<!-- Feature Name -->

## Status

<!-- Not Started|In Progress|Complete -->

Not Started

## Goals

<!-- Goals & requirements -->

## Notes

<!-- Any extra notes -->

## History

<!-- Keep this updated. Earliest to latest -->

- **User Dashboard** (`context/features/03-user-dashboard.md`) — merged 2026-09-04
  (2887d58). Replaced the `/_app/` placeholder in `frontend/src/routes/_app.index.tsx`
  with a document list fetched via `documentsApi.list()` and rendered through the
  existing `DataTable` component (name/doctype/status badge/updated columns, matching
  `_app.admin.documents.tsx`'s pattern). Added a per-row "Chat"/"Selected" button that
  sets local `activeDocument` state — the hook `04-document-chat.md` builds on next.
  No backend changes.
