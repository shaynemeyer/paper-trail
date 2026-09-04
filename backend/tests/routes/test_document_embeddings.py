import pytest
from app import embeddings
from app.config import EMBEDDING_DIM


@pytest.fixture(autouse=True)
def fake_embed_text(monkeypatch):
    """Avoid calling a real Ollama instance in tests."""

    async def _fake_embed_text(text: str) -> list[float]:
        # Deterministic stand-in vector matching the column's fixed dimension.
        return [float(len(text) % 7)] * EMBEDDING_DIM

    monkeypatch.setattr(embeddings, "embed_text", _fake_embed_text)
    import app.routes.documents as documents_route

    monkeypatch.setattr(documents_route, "embed_text", _fake_embed_text)


async def test_embed_document(client, auth_headers, sample_documents):
    document_id = sample_documents[0].id
    response = await client.post(
        f"/api/documents/{document_id}/embed", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["id"] == document_id


async def test_embed_document_not_found(client, auth_headers):
    response = await client.post("/api/documents/999/embed", headers=auth_headers)
    assert response.status_code == 404


async def test_search_documents(client, auth_headers, sample_documents):
    for document in sample_documents:
        await client.post(f"/api/documents/{document.id}/embed", headers=auth_headers)

    response = await client.get("/api/documents/search?q=invoice", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
