# Current Feature: Document Upload UI

<!-- Feature Name -->

## Status

<!-- Not Started|In Progress|Complete -->

In Progress

## Goals

<!-- Goals & requirements -->

- Add a separate "Upload PDF" button + Dialog on `_app.admin.documents.tsx`, distinct from the
  existing "New Document" dialog (incompatible field shapes: upload has no doctype/status, JSON
  create has no file/tags).
- New local state: `uploadDialogOpen`, `uploadForm` (`name`, `description`, `document_source`,
  `tagsInput`), `uploadFile: File | null` (kept separate — file inputs are uncontrolled).
- `emptyUploadForm` constant mirroring `emptyForm`.
- `openUpload()` mirroring `openCreate()`, wired to the trigger button.
- `uploadMutation = useMutation({ mutationFn: documentsApi.upload, ... })` following the existing
  `createMutation` convention: `onSuccess` → invalidate `['documents']`, `toast.success`, close
  dialog, reset form/file; `onError` → `toast.error(err.message)`.
- `handleUploadSubmit(e)` — guard on `uploadFile` present and `uploadFile.type ===
  'application/pdf'` (client-side only; server 400 stays authoritative), then
  `uploadMutation.mutate({ file, name, description, document_source: uploadForm.document_source
  || undefined, tags: <split/trim/filter tagsInput> })`.
- New JSX: second `<Dialog>` next to the existing one, triggered by "Upload PDF" button
  (`variant="outline"`). Fields: PDF file (`<Input type="file" accept="application/pdf" required>`),
  Name, Description, Source (optional), Tags (comma-separated, optional). No Doctype/Status field.
  Submit button shows "Uploading…" and is disabled while `uploadMutation.isPending`.

## Notes

<!-- Any extra notes -->

- Spec: `context/features/02-document-upload-ui.md`. Depends on `01-document-upload-api-client`
  (merged). Full background: `docs/plan-pdf-upload.md`.
- Out of scope: drag-and-drop, multi-file batch upload, progress bars, adding a `tags` column to
  the documents table.
- Testing: no frontend test runner — verify manually per the spec's Testing section (upload flow,
  Embed still works, `/documents/{id}/markdown` returns text, non-PDF file rejected client-side,
  `bun run lint` + `bun run build` pass).

## History

<!-- Keep this updated. Earliest to latest -->

- **Document Upload API Client** (`context/features/01-document-upload-api-client.md`) — merged
  2026-09-04 (afa44b3). Added `requestForm<T>` to `frontend/src/lib/api.ts` for multipart uploads,
  the `UploadDocumentInput` type, and `documentsApi.upload`, wiring the frontend to the existing
  `POST /api/documents/upload` backend route. No backend or UI changes.
