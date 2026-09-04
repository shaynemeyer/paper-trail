import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app import chat as chat_module
from app import embeddings
from app.config import EMBEDDING_DIM
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


@pytest.fixture(autouse=True)
def fake_embed_text(monkeypatch):
    async def _fake_embed_text(text: str) -> list[float]:
        return [float(len(text) % 7)] * EMBEDDING_DIM

    monkeypatch.setattr(embeddings, "embed_text", _fake_embed_text)
    import app.routes.chat as chat_route

    monkeypatch.setattr(chat_route, "embed_text", _fake_embed_text)


@pytest.fixture(autouse=True)
def fake_ask(monkeypatch):
    async def _fake_ask(question: str, context: str) -> str:
        assert context  # the LLM only ever sees retrieved chunk text
        return f"Answer to: {question}"

    monkeypatch.setattr(chat_module, "ask", _fake_ask)
    import app.routes.chat as chat_route

    monkeypatch.setattr(chat_route, "ask", _fake_ask)


@pytest.fixture
async def document_with_chunks(async_session: AsyncSession):
    document = Document(name="Lease Agreement", description="A lease")
    async_session.add(document)
    await async_session.commit()
    await async_session.refresh(document)

    chunks = [
        DocumentChunk(document_id=document.id, chunk_index=0, content="Rent is $2000/mo."),
        DocumentChunk(document_id=document.id, chunk_index=1, content="Lease term is 12 months."),
    ]
    for chunk in chunks:
        async_session.add(chunk)
    await async_session.commit()
    return document


async def test_chat_with_document(client, auth_headers, document_with_chunks):
    response = await client.post(
        f"/api/documents/{document_with_chunks.id}/chat",
        json={"message": "How much is rent?"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Answer to: How much is rent?"
    assert len(body["chunk_ids"]) == 2


async def test_chat_document_not_found(client, auth_headers):
    response = await client.post(
        "/api/documents/999/chat",
        json={"message": "Anything?"},
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_chat_document_with_no_chunks(client, auth_headers, sample_documents):
    document_id = sample_documents[0].id
    response = await client.post(
        f"/api/documents/{document_id}/chat",
        json={"message": "Anything?"},
        headers=auth_headers,
    )
    assert response.status_code == 404
