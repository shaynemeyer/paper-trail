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

- **Document Upload UI** (`context/features/02-document-upload-ui.md`) — merged 2026-09-04
  (92c7aa0). Added a separate "Upload PDF" dialog to
  `frontend/src/routes/_app.admin.documents.tsx` (file, name, description, source, tags — no
  doctype/status), wired via `uploadMutation` to `documentsApi.upload` following the existing
  `createMutation` convention. No backend changes.
