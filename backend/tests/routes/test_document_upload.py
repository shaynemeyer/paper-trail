import pytest
import pymupdf
from app import embeddings
from app.config import EMBEDDING_DIM


@pytest.fixture
def pdf_bytes() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello world, this is a test document about invoices.")
    return doc.tobytes()


@pytest.fixture(autouse=True)
def fake_embed_text(monkeypatch):
    async def _fake_embed_text(text: str) -> list[float]:
        return [float(len(text) % 7)] * EMBEDDING_DIM

    monkeypatch.setattr(embeddings, "embed_text", _fake_embed_text)
    import app.routes.documents as documents_route

    monkeypatch.setattr(documents_route, "embed_text", _fake_embed_text)


async def test_upload_document(client, auth_headers, pdf_bytes):
    response = await client.post(
        "/api/documents/upload",
        files={"file": ("invoice.pdf", pdf_bytes, "application/pdf")},
        data={
            "name": "Uploaded Invoice",
            "description": "Uploaded via test",
            "tags": "finance, invoice",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Uploaded Invoice"
    assert body["doctype"] == "pdf"
    assert body["tags"] == ["finance", "invoice"]
    assert body["status"] == "pending"
    assert body["raw_url"] == f"/api/documents/{body['id']}/raw"
    assert body["markdown_url"] == f"/api/documents/{body['id']}/markdown"


async def test_upload_rejects_non_pdf(client, auth_headers):
    response = await client.post(
        "/api/documents/upload",
        files={"file": ("notes.txt", b"not a pdf", "text/plain")},
        data={"name": "Notes", "description": "Not a PDF"},
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_get_document_raw_and_markdown(client, auth_headers, pdf_bytes):
    upload = await client.post(
        "/api/documents/upload",
        files={"file": ("invoice.pdf", pdf_bytes, "application/pdf")},
        data={"name": "Invoice", "description": "For raw/markdown fetch"},
        headers=auth_headers,
    )
    document_id = upload.json()["id"]

    raw_response = await client.get(
        f"/api/documents/{document_id}/raw", headers=auth_headers
    )
    assert raw_response.status_code == 200
    assert raw_response.headers["content-type"] == "application/pdf"

    markdown_response = await client.get(
        f"/api/documents/{document_id}/markdown", headers=auth_headers
    )
    assert markdown_response.status_code == 200
    assert "invoices" in markdown_response.text
