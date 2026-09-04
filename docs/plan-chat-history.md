# Plan: Persist Document Chat History

## Problem

`POST /api/documents/{id}/chat` (`backend/app/routes/chat.py`) is stateless —
it takes a single `message`, retrieves fresh chunks, and returns an answer.
Nothing is stored, so refreshing the page (or the dashboard chat panel added
in `docs/plan-user-dashboard-chat.md`) loses the conversation. This plan adds
durable, per-user, per-document chat history.

Depends on: `docs/plan-user-dashboard-chat.md` (the chat panel this attaches
to must exist first).

## Goals

- Every question and answer for a document is persisted, tied to the user
  who asked it.
- Reopening a document's chat panel shows prior turns for that user, not a
  blank slate.
- A user can clear their own history for a document.
- Users only ever see their own chat history — not other users' questions
  about the same document (chat content is intentionally private; there is
  no shared "team chat" concept for documents).

## Changes

### 1. Backend: `ChatMessage` model (`backend/app/models/chat_message.py`)

Follows the four-schema pattern used elsewhere (`document_chunk.py` for the
table shape, `user.py` for `*Read`):

```python
class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    user_sub: str = Field(index=True)  # JWT `sub` claim, not a users.id FK —
                                        # consistent with how chat.py already
                                        # logs user_id=user.get("sub")
    role: ChatRole
    content: str
    chunk_ids: list[int] | None = Field(default=None, sa_column=Column(ARRAY(Integer)))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

class ChatMessageRead(SQLModel):
    id: int
    role: ChatRole
    content: str
    chunk_ids: list[int] | None
    created_at: datetime
```

No `ChatMessageCreate`/`ChatMessageUpdate` — messages are only ever created
as a side effect of the chat route (below), never via a direct client POST,
and are never edited.

Table is picked up automatically by the existing `SQLModel.metadata.create_all`
in `main.py`'s lifespan hook — no migration needed.

### 2. Backend: persist turns in the chat route

In `chat_with_document` (`backend/app/routes/chat.py`), after computing
`answer`, insert two `ChatMessage` rows in the same session before returning:
one `role=user` with `content=body.message`, one `role=assistant` with
`content=answer` and `chunk_ids=[c.id for c in chunks]`. Both get
`user_sub=user.get("sub")`.

### 3. Backend: history endpoints

Add to `chat.py`:

- `GET /documents/{document_id}/chat/history` — `require_user`; returns
  `list[ChatMessageRead]` filtered to `document_id` **and** `user_sub ==
  user.get("sub")`, ordered by `created_at`.
- `DELETE /documents/{document_id}/chat/history` — `require_user`; deletes
  only the current user's `ChatMessage` rows for that document. Returns 204.

### 4. Frontend: wire history into the chat panel (depends on 1–3)

- Extend `chatApi` in `src/lib/api.ts`:
  ```ts
  export interface ChatMessage {
    id: number
    role: "user" | "assistant"
    content: string
    chunk_ids: number[] | null
    created_at: string
  }

  export const chatApi = {
    ask: (documentId: number, message: string) => /* existing */,
    history: (documentId: number) =>
      request<ChatMessage[]>(`/documents/${documentId}/chat/history`),
    clearHistory: (documentId: number) =>
      request<void>(`/documents/${documentId}/chat/history`, { method: "DELETE" }),
  }
  ```
- In `document-chat.tsx`, load history via `useQuery({ queryKey: ["chat-history", documentId], queryFn: () => chatApi.history(documentId) })`
  and render it as the initial message list instead of starting empty.
- On successful `ask`, invalidate `["chat-history", documentId]` (standard
  mutation shape) instead of manually appending to local state, so the
  panel and the persisted record can't drift apart.
- Add a "Clear history" action wired to `clearHistory`, following the same
  confirm pattern as document/user delete (`AlertDialog`).

## Out of scope

- No cross-document search over chat history.
- No admin visibility into other users' chat history — if that's ever
  needed, it's a separate, explicitly-scoped decision (privacy-sensitive).
- No retention/expiry policy — history accumulates indefinitely until a
  user clears it themselves.
- No streaming responses — this only changes what's persisted, not how the
  answer is produced.

## Testing

Per `context/testing-instructions.md`:

- Backend: a test that `POST .../chat` results in two new `ChatMessage`
  rows (user + assistant, correct `user_sub`); a test that `GET
  .../chat/history` only returns the requesting user's own messages, not
  another user's; a test that `DELETE .../chat/history` removes only the
  caller's rows and returns 204; 401 case for all three routes without auth.
  Reuse the `app.embeddings.embed_text` monkeypatch pattern from
  `test_document_embeddings.py` so these don't need live Ollama.
- Frontend: manual verification — ask a question, refresh the page, confirm
  history reloads; clear history and confirm it empties; confirm a second
  user's token doesn't see the first user's history for the same document.
