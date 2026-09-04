# Plan: User Dashboard + Document Chat

## Problem

`frontend/src/routes/_app.index.tsx` is a placeholder ("Your dashboard is
coming soon") — every user lands there after login and sees nothing useful.
Meanwhile the backend already supports asking questions about a document's
content (`POST /api/documents/{id}/chat`, `backend/app/routes/chat.py`), but
no frontend code calls it — there's no `chatApi` in `src/lib/api.ts` and no
chat UI anywhere.

This plan replaces the placeholder with a real dashboard: a list of the
user's documents, and the ability to pick one and chat with it.

## Goals

- A user landing on `/` sees their documents, not a "coming soon" message.
- Selecting a document opens an interactive chat grounded in that document's
  content, using the existing `/documents/{id}/chat` endpoint.
- No backend changes — the chat endpoint, auth, and retrieval already exist.

## Changes

### 1. User dashboard (`frontend/src/routes/_app.index.tsx`)

Replace the placeholder with a document list for the current user, using the
existing `documentsApi.list()` and the same `DataTable` pattern already used
in `_app.admin.documents.tsx`. Each row is selectable (button or row click) to
become the "active" document for chat. Keep this route's existing path
(`/_app/`) — only the component changes.

### 2. Document chat (depends on 1)

- Add a `chatApi` to `src/lib/api.ts`, sibling to `documentsApi`/`usersApi`:
  ```ts
  export interface ChatResponse {
    answer: string
    chunk_ids: number[]
  }

  export const chatApi = {
    ask: (documentId: number, message: string) =>
      request<ChatResponse>(`/documents/${documentId}/chat`, {
        method: "POST",
        body: JSON.stringify({ message }),
      }),
  }
  ```
- Add a chat panel component (custom, not a shadcn primitive, so it belongs
  under `src/components/documents/document-chat.tsx` per
  `context/coding-standards.md`) that takes the selected document and renders
  a simple message list + input, calling `chatApi.ask` via a
  `useMutation` following the standard mutation shape (`onError` →
  `toast.error(err.message)`; no query invalidation needed since chat isn't
  cached state).
- Wire it into the dashboard from step 1: selecting a document shows the chat
  panel for it (e.g. in a `Drawer`/side panel, consistent with existing
  admin-page patterns).

## Out of scope

- No changes to `/documents/search` (still not wired into any UI).
- No persistence of chat history — each session starts fresh.
- No changes to the admin documents/users pages.
