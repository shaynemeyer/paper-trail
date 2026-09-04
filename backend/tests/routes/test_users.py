async def test_get_users_requires_auth(client):
    response = await client.get("/api/users")
    assert response.status_code == 401


async def test_get_users_requires_admin(client, auth_headers, sample_users):
    response = await client.get("/api/users", headers=auth_headers)
    assert response.status_code == 403


async def test_get_users_as_admin(client, admin_headers, sample_users):
    response = await client.get("/api/users", headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_create_user(client, admin_headers):
    response = await client.post(
        "/api/users",
        json={"email": "carol@example.com", "name": "Carol", "role": "user"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    assert response.json()["email"] == "carol@example.com"


async def test_get_user_not_found(client, admin_headers):
    response = await client.get("/api/users/999", headers=admin_headers)
    assert response.status_code == 404


async def test_patch_user_role(client, admin_headers, sample_users):
    user_id = sample_users[1].id
    response = await client.patch(
        f"/api/users/{user_id}", json={"role": "admin"}, headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


async def test_delete_user_requires_admin(client, auth_headers, sample_users):
    user_id = sample_users[0].id
    response = await client.delete(f"/api/users/{user_id}", headers=auth_headers)
    assert response.status_code == 403


async def test_delete_user_as_admin(client, admin_headers, sample_users):
    user_id = sample_users[0].id
    response = await client.delete(f"/api/users/{user_id}", headers=admin_headers)
    assert response.status_code == 204
