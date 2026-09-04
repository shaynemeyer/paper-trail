# Document Upload API Client

**Status:** Complete — merged 2026-09-04 (afa44b3)

**Depends on:** none

## Context

The backend already fully supports PDF ingestion via `POST /api/documents/upload`
(`backend/app/routes/documents.py`, `upload_document`): it saves the raw PDF,
extracts markdown (`app/pdf.py`), chunks it (`app/chunking.py`), embeds each
chunk via Ollama (`app/embeddings.py`), stores `DocumentChunk` rows, and forces
`status = "pending"` once processing finishes. Nothing in the frontend can call
it yet — `frontend/src/lib/api.ts`'s `request<T>()` helper always sets
`Content-Type: application/json`, which breaks multipart uploads (the browser
must set the `Content-Type`/boundary itself for `FormData` bodies). This
feature adds the missing client-side plumbing only; no UI changes.

Full context: `docs/plan-pdf-upload.md`. This spec covers step "Changes →
`frontend/src/lib/api.ts`" of that plan.

## Goals

- Add `requestForm<T>(path, formData)` to `frontend/src/lib/api.ts`, as a
  sibling to `request()` (do not modify `request()` itself — it's used
  everywhere for JSON bodies):
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
  No `Content-Type` header is set manually. Same `Authorization` + `ApiError`
  handling as `request()` so existing `toast.error(err.message)` call sites
  keep working unchanged.
- Add an `UploadDocumentInput` interface next to `DocumentInput`:
  ```ts
  export interface UploadDocumentInput {
    file: File
    name: string
    description: string
    document_source?: string
    tags: string[]
  }
  ```
- Add `documentsApi.upload`:
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

## Notes

- `document_source` is only appended when truthy — the server's `Form(None)`
  default already handles absence, and an empty string would needlessly
  override it.
- `tags: string[]` is joined to a comma-separated string here, matching the
  server's `tags: str = Form("")` + server-side split
  (`backend/app/routes/documents.py`).
- No backend changes in this feature — `/documents/upload` already exists and
  is unmodified.

## Testing

Per `context/testing-instructions.md`, the frontend has no test runner
configured — verify manually rather than inventing a Vitest/Jest setup:

1. `bun run build` (`tsc -b && vite build`) must pass with no type errors —
   this is the primary check for a types-and-plumbing-only change with no UI
   to click through yet.
2. `bun run lint` (oxlint) must pass.
3. Sanity-check `documentsApi.upload` from the browser console against a
   running backend (`./doit.sh db-up && ./doit.sh run` in `backend/`, `bun dev`
   in `frontend/`), e.g.:
   ```js
   const input = document.createElement('input')
   ```
   or simpler: temporarily call it from a scratch component/dev tool with a
   real `File` object and confirm a 201 + `DocumentRead` JSON comes back, and
   that the new document appears via `GET /documents`. This manual check can
   be dropped once feature `02-document-upload-ui` provides a real UI trigger
   — it exists here only to validate this feature in isolation.
