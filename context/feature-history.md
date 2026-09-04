# Feature History

<!-- Archive of completed features, oldest to newest -->

- **Document Upload API Client** (`context/features/01-document-upload-api-client.md`) — merged
  2026-09-04 (afa44b3). Added `requestForm<T>` to `frontend/src/lib/api.ts` for multipart uploads,
  the `UploadDocumentInput` type, and `documentsApi.upload`, wiring the frontend to the existing
  `POST /api/documents/upload` backend route. No backend or UI changes.
