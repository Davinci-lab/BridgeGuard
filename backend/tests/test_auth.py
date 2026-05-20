def register_user(client, email="alice@example.com", password="StrongPass123!"):
    response = client.post(
        "/api/v2/auth/register",
        json={"email": email, "password": password, "project_name": "Alice Project"},
    )
    assert response.status_code == 201
    return response.json()


def login_user(client, email="alice@example.com", password="StrongPass123!"):
    response = client.post(
        "/api/v2/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_login_and_me(client):
    registered = register_user(client, "alice@example.com")

    assert registered["email"] == "alice@example.com"
    assert registered["is_active"] is True
    assert "hashed_password" not in registered

    headers = login_user(client, "alice@example.com")
    me = client.get("/api/v2/auth/me", headers=headers)

    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.com"


def test_register_duplicate_email_returns_conflict(client):
    register_user(client, "dupe@example.com")

    response = client.post(
        "/api/v2/auth/register",
        json={"email": "dupe@example.com", "password": "StrongPass123!"},
    )

    assert response.status_code == 409


def test_projects_require_auth_and_registration_creates_default_project(client):
    register_user(client, "project-owner@example.com")

    assert client.get("/api/v2/projects").status_code == 401

    headers = login_user(client, "project-owner@example.com")
    response = client.get("/api/v2/projects", headers=headers)

    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 1
    assert projects[0]["name"] == "Alice Project"
