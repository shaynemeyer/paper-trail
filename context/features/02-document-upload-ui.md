# Document Upload UI

**Status:** Not Started

**Depends on:** 01-document-upload-api-client

## Context

With `documentsApi.upload` in place (feature `01-document-upload-api-client`),
the admin documents page still has no way to trigger it —
`frontend/src/routes/_app.admin.documents.tsx` only has a JSON "New Document"
dialog wired to `documentsApi.create`. This feature adds the actual "Upload
PDF" UI: a button, a dialog with a file picker + metadata fields, and the
mutation wiring to call `documentsApi.upload`.

Full context: `docs/plan-pdf-upload.md`. This spec covers step "Changes →
`frontend/src/routes/_app.admin.documents.tsx`" of that plan.

## Goals

Add a **separate "Upload PDF" button + Dialog**, distinct from the existing
"New Document" dialog — the two flows have incompatible field shapes (JSON
create sends `doctype`/`status` and no file/tags; upload sends a required
`file` + `tags` and no `doctype`/`status`, since the server hardcodes
`doctype="pdf"` and forces `status="pending"` after processing). A second
small dialog is a clearer diff than branching the existing form.

1. Import `UploadDocumentInput` alongside the existing type imports from
   `@/lib/api`.
2. New local state, next to `dialogOpen`/`editing`/`form`:
   - `uploadDialogOpen: boolean`
   - `uploadForm: { name, description, document_source, tagsInput }` (raw
     comma-separated string; split into `string[]` at submit time)
   - `uploadFile: File | null` — kept separate from `uploadForm` because a
     file `<input>` is uncontrolled and can't be reset via `value`
3. `emptyUploadForm` constant mirroring the existing `emptyForm`.
4. `openUpload()` — resets `uploadForm`/`uploadFile` and opens the dialog
   (mirrors the existing `openCreate()`); wire it to the new trigger button's
   `onClick`.
5. `uploadMutation = useMutation({ mutationFn: documentsApi.upload, ... })`
   following the exact `onSuccess`/`onError` convention already used by
   `createMutation`: invalidate `['documents']`, `toast.success(...)`, close
   the dialog, reset `uploadForm`/`uploadFile`; `onError` →
   `toast.error(err.message)`.
6. `handleUploadSubmit(e)` — guards on `uploadFile` being present and
   `uploadFile.type === 'application/pdf'` (client-side pre-flight only; the
   server's 400 stays authoritative), then calls
   `uploadMutation.mutate({ file, name, description, document_source: uploadForm.document_source || undefined, tags: <split/trim/filter of tagsInput> })`.
7. New JSX: a second `<Dialog>` placed next to the existing one in the
   header's flex row, triggered by an "Upload PDF" button (`variant="outline"`
   to sit secondary to "New Document"). Form fields:
   - PDF file — `<Input type="file" accept="application/pdf" required>` (the
     existing `Input` wrapper already carries `file:*` Tailwind styling, per
     `components/ui/input.tsx` — no raw unstyled `<input>` needed)
   - Name
   - Description
   - Source (optional)
   - Tags (comma-separated, optional)

   Deliberately **no** Doctype or Status field — showing either would be
   misleading since the server ignores/overrides them. Submit button shows
   "Uploading…" and is `disabled` while `uploadMutation.isPending`, matching
   the disable-only pending convention already used for the Embed button — no
   progress bar (native `fetch` doesn't support upload progress, and it's out
   of scope).

## Out of scope

Drag-and-drop, multi-file batch upload, upload progress bars, and adding a
`tags` column to the documents table.

## Testing

Per `context/testing-instructions.md`, the frontend has no test runner
configured — verify manually:

1. `cd backend && ./doit.sh db-up && ./doit.sh run` (Ollama running locally
   with `qwen3-embedding:4b` pulled, per `OLLAMA_BASE_URL`/`EMBEDDING_MODEL`).
2. `cd frontend && bun dev`.
3. On the admin documents page, click "Upload PDF", fill in name/description,
   pick a real PDF file, submit. Confirm:
   - A success toast appears and the new document shows up in the table with
     status "pending".
   - Clicking "Embed" still works on it (existing feature — sanity check
     nothing broke).
   - `GET /api/documents/{id}/markdown` (browser or curl with a bearer token)
     returns extracted text, confirming parsing ran end-to-end.
4. Negative test: try uploading a non-PDF file — the client-side guard should
   toast an error before any request is sent.
5. `bun run lint` and `bun run build` (`tsc -b && vite build`) must pass with
   no type errors.
