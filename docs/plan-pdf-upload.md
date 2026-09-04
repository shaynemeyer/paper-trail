# Add "Upload PDF" to the frontend documents page

**Progress:** Step 1 (`frontend/src/lib/api.ts`) is done — see
`context/features/01-document-upload-api-client.md` (merged 2026-09-04). Step 2
(`_app.admin.documents.tsx`) is tracked in `context/features/02-document-upload-ui.md`.

## Context

The backend already fully supports PDF ingestion: `POST /api/documents/upload`
(`backend/app/routes/documents.py`, `upload_document`) saves the raw PDF, extracts
markdown (`app/pdf.py`), chunks it (`app/chunking.py`), embeds each chunk via Ollama
(`app/embeddings.py`), and stores `DocumentChunk` rows — it forces
`status = "pending"` server-side once processing finishes. None of this is exposed in
the UI: the frontend's only document-creation path is the JSON `POST /documents`
form in `frontend/src/routes/_app.admin.documents.tsx`, which has no file input and
no way to hit `/documents/upload`. This plan adds that missing frontend path so a
user can actually upload and parse a PDF from the admin UI.

Backend is not touched — this is a frontend-only change.

## Approach

Add a **separate "Upload PDF" button + Dialog**, distinct from the existing
"New Document" dialog, rather than merging into it. The two flows have
incompatible field shapes: JSON create sends `doctype`/`status` and no file/tags;
upload sends a required `file` + `tags` and no `doctype`/`status` (the server
ignores/overrides status anyway). A second small dialog is a smaller, clearer diff
than branching the existing form.

## Changes

### `frontend/src/lib/api.ts`

1. Add a multipart-aware sibling to `request()` (which always sets
   `Content-Type: application/json` and can't be reused as-is):

   ```ts
   async function requestForm<T>(path: string, formData: FormData): Promise<T> {
     const token = getToken()
     const response = await fetch(`${API_URL}${path}`, {
       method: "POST",
       headers: token ? { Authorization: `Bearer ${token}` } : {},
       body: formData,
     })
     if (!response.ok) {
       const body = await response.json().catch(() => null)
       throw new ApiError(response.status, body?.detail ?? response.statusText)
     }
     return response.json()
   }
   ```

   No `Content-Type` is set manually — the browser must supply the multipart
   boundary. Same `Authorization` + `ApiError` handling as `request()`, so existing
   `toast.error(err.message)` call sites keep working unchanged.

2. Add `UploadDocumentInput` next to `DocumentInput`:

   ```ts
   export interface UploadDocumentInput {
     file: File
     name: string
     description: string
     document_source?: string
     tags: string[]
   }
   ```

3. Add `documentsApi.upload`:

   ```ts
   upload: (data: UploadDocumentInput) => {
     const formData = new FormData()
     formData.append("file", data.file)
     formData.append("name", data.name)
     formData.append("description", data.description)
     if (data.document_source) formData.append("document_source", data.document_source)
     formData.append("tags", data.tags.join(","))
     return requestForm<Document>("/documents/upload", formData)
   },
   ```

### `frontend/src/routes/_app.admin.documents.tsx`

1. Import `UploadDocumentInput` alongside the existing type imports from `@/lib/api`.

2. New local state (next to `dialogOpen`/`editing`/`form`):
   - `uploadDialogOpen` (boolean)
   - `uploadForm` — `{ name, description, document_source, tagsInput }` (raw
     comma-separated string, split into `string[]` at submit time)
   - `uploadFile: File | null` — held separately because a file `<input>` is
     uncontrolled and can't be reset via `value`

3. `emptyUploadForm` constant mirroring `emptyForm`.

4. `openUpload()` — resets `uploadForm`/`uploadFile` and opens the dialog (mirrors
   the existing `openCreate()`); wire it to the new trigger button's `onClick`.

5. `uploadMutation = useMutation({ mutationFn: documentsApi.upload, ... })` following
   the exact `onSuccess`/`onError` convention already used by `createMutation`:
   invalidate `['documents']`, `toast.success(...)`, close the dialog, reset
   `uploadForm`/`uploadFile`; `onError` → `toast.error(err.message)`.

6. `handleUploadSubmit(e)` — guards on `uploadFile` being present and
   `uploadFile.type === 'application/pdf'` (client-side pre-flight only; the
   server's 400 stays authoritative), then calls
   `uploadMutation.mutate({ file, name, description, document_source: ... || undefined, tags: split/trim/filter })`.

7. New JSX: a second `<Dialog>` placed next to the existing one in the header's
   flex row, triggered by an "Upload PDF" button (`variant="outline"` to sit
   secondary to "New Document"). Form fields: PDF file (`<Input type="file"
   accept="application/pdf" required>` — the existing `Input` wrapper already
   carries `file:*` Tailwind styling, confirmed in `components/ui/input.tsx`),
   Name, Description, Source (optional), Tags (comma-separated, optional).
   Deliberately **no** Doctype or Status field — the server hardcodes
   `doctype="pdf"` and forces `status="pending"` after processing, so showing
   either would be misleading. Submit button shows `Uploading…` and is disabled
   while `uploadMutation.isPending`, matching the disable-only pending convention
   already used for the Embed button — no progress bar (native `fetch` doesn't
   support upload progress, and it's out of scope).

## Out of scope

Drag-and-drop, multi-file batch upload, upload progress bars, and adding a `tags`
column to the documents table are all explicitly excluded — none are needed for
this feature and none exist elsewhere in the codebase to extend.

## Verification

1. `cd backend && ./doit.sh db-up && ./doit.sh run` (ensure Ollama is running
   locally with `qwen3-embedding:4b` pulled, per `OLLAMA_BASE_URL`/`EMBEDDING_MODEL`).
2. `cd frontend && bun dev`.
3. In the admin documents page, click "Upload PDF", fill in name/description, pick
   a real PDF file, submit. Confirm:
   - A success toast appears and the new document shows up in the table with
     status "pending".
   - Clicking "Embed" still works on it (existing feature, sanity check nothing
     broke).
   - `GET /api/documents/{id}/markdown` (e.g. via the browser or curl with a
     bearer token) returns extracted text, confirming parsing ran.
4. Negative test: try uploading a non-PDF file — expect the client-side guard to
   toast an error before any request is sent.
5. `bun run lint` and `bun run build` (`tsc -b && vite build`) to catch any type
   errors in the new code.
