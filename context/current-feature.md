# Current Feature: Document Chat

## Status

In Progress

## Goals

- Add `chatApi` and `ChatResponse` to `frontend/src/lib/api.ts`, following the existing API object pattern and posting messages to `/documents/{documentId}/chat`.
- Add `frontend/src/components/documents/document-chat.tsx` with a message list and input for the selected document.
- Submit questions with `useMutation`, append successful answers to local message state, and show `toast.error(err.message)` on errors.
- Show the chat panel from the user dashboard when a document is selected, using a drawer or side-panel pattern consistent with existing admin pages.
- Keep this frontend-only; make no backend changes.

## Notes

- Spec: `context/features/04-document-chat.md`.
- Depends on completed feature `03-user-dashboard`.
- The backend chat endpoint, authentication, and retrieval flow already exist.
- Chat history is in-memory only and starts fresh when a document is reselected.
- Out of scope: document search changes, persisted chat history, and changes to admin document or user pages.
- Manual validation should confirm successful answers render and API failures, including documents without embedded chunks, show an error toast.

## History

- **Document Chat** (`context/features/04-document-chat.md`) — loaded 2026-09-04.
