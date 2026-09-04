# Document Chat

**Status:** Not Started
**Depends on:** 03-user-dashboard

## Context

Source plan: `docs/plan-user-dashboard-chat.md`, section "2. Document chat
(depends on 1)".

The backend already supports asking questions about a document's content:
`POST /api/documents/{document_id}/chat` in
`backend/app/routes/chat.py`:

```python
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    chunk_ids: list[int]


@router.post("/documents/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(
    document_id: int,
    body: ChatRequest,
    session: AsyncSession = Depends(get_session),
    user: dict = Depends(require_user),
):
    """Answer a question about a document, grounded only in its embedded chunks.

    Returns:
        200: Answered
        404: Document not found or has no embedded chunks yet
        401: Unauthorized
    """
```

No frontend code calls this endpoint yet — there is no `chatApi` in
`frontend/src/lib/api.ts` and no chat UI anywhere. `frontend/src/lib/api.ts`
currently exports `documentsApi` and `usersApi` as the `*Api` object
pattern to follow, built on the shared `request<T>()` wrapper.

## Goals

- Add a `chatApi` to `frontend/src/lib/api.ts`, sibling to
  `documentsApi`/`usersApi`:

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

- Add a chat panel component at
  `frontend/src/components/documents/document-chat.tsx` (custom component,
  not a shadcn primitive, per `context/coding-standards.md`'s
  `components/{domain}/{component-name}.tsx` convention). It takes the
  selected document as a prop and renders a message list + input.
- Wire `chatApi.ask` via `useMutation` following the standard mutation shape
  from `context/coding-standards.md`: `onError` → `toast.error(err.message)`.
  No `onSuccess` query invalidation needed — chat isn't cached/persisted
  state, so on success just append the answer to the local message list.
- Wire the panel into the dashboard from `03-user-dashboard.md`: selecting a
  document (the state added in that spec) shows the chat panel for it, e.g.
  in a `Drawer`/side panel, consistent with existing admin-page patterns.
- No backend changes — the endpoint, auth, and retrieval already exist.

## Notes

- Chat history is in-memory only for the session — no persistence, each
  chat starts fresh when a document is (re)selected.
- Out of scope (per the plan): no changes to `/documents/search`, no
  persistence of chat history, no changes to the admin documents/users pages.

## Testing

- Manual: from the dashboard, select a document, ask a question in the chat
  panel, confirm the answer renders. Confirm error toast shows if the
  document has no embedded chunks (backend 404) or on other API errors.
- No backend tests needed (no backend changes).
