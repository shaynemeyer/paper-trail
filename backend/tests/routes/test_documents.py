async def test_get_documents_requires_auth(client):
    response = await client.get("/api/documents")
    assert response.status_code == 401


async def test_get_documents(client, auth_headers, sample_documents):
    response = await client.get("/api/documents", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 3


async def test_create_document(client, auth_headers):
    response = await client.post(
        "/api/documents",
        json={
            "name": "Invoice #1025",
            "description": "Q4 invoice for office supplies",
            "status": "draft",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Invoice #1025"
    assert response.json()["doctype"] == "pdf"


async def test_get_document_not_found(client, auth_headers):
    response = await client.get("/api/documents/999", headers=auth_headers)
    assert response.status_code == 404


async def test_patch_document(client, auth_headers, sample_documents):
    document_id = sample_documents[0].id
    response = await client.patch(
        f"/api/documents/{document_id}",
        json={"status": "approved"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


async def test_delete_document_requires_admin(client, auth_headers, sample_documents):
    document_id = sample_documents[0].id
    response = await client.delete(f"/api/documents/{document_id}", headers=auth_headers)
    assert response.status_code == 403


async def test_delete_document_as_admin(client, admin_headers, sample_documents):
    document_id = sample_documents[0].id
    response = await client.delete(f"/api/documents/{document_id}", headers=admin_headers)
    assert response.status_code == 204
