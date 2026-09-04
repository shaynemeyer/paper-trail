# Feature History

<!-- Archive of completed features, oldest to newest -->

- **Document Upload API Client** (`context/features/01-document-upload-api-client.md`) — merged
  2026-09-04 (afa44b3). Added `requestForm<T>` to `frontend/src/lib/api.ts` for multipart uploads,
  the `UploadDocumentInput` type, and `documentsApi.upload`, wiring the frontend to the existing
  `POST /api/documents/upload` backend route. No backend or UI changes.


- **Document Upload UI** (`context/features/02-document-upload-ui.md`) — merged 2026-09-04
  (92c7aa0). Added a separate "Upload PDF" dialog to
  `frontend/src/routes/_app.admin.documents.tsx` (file, name, description, source, tags — no
  doctype/status), wired via `uploadMutation` to `documentsApi.upload` following the existing
  `createMutation` convention. No backend changes.
