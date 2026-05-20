from app.models.payment_models import ApiKey


def register_and_login(client, email="demo@bridgeguard.local", password="StrongPass123!"):
    response = client.post(
        "/api/v2/auth/register",
        json={"email": email, "password": password, "project_name": "Premium Project"},
    )
    assert response.status_code == 201

    login = client.post(
        "/api/v2/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def get_first_project_id(client, headers):
    response = client.get("/api/v2/projects", headers=headers)
    assert response.status_code == 200
    return response.json()[0]["id"]


def test_admin_can_create_project_scoped_api_key(client):
    headers = register_and_login(client)
    project_id = get_first_project_id(client, headers)

    response = client.post(
        "/api/v2/api-keys",
        headers=headers,
        json={"project_id": project_id, "plan": "premium"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["key"].startswith("bg_live_")
    assert body["plan"] == "premium"
    assert body["project_id"] == project_id
    assert body["is_active"] is True


def test_non_admin_cannot_create_api_key(client):
    headers = register_and_login(client, email="operator@example.com")
    project_id = get_first_project_id(client, headers)

    response = client.post(
        "/api/v2/api-keys",
        headers=headers,
        json={"project_id": project_id, "plan": "premium"},
    )

    assert response.status_code == 403


def test_premium_connector_evaluate_requires_api_key(client):
    response = client.post("/api/v2/connectors/mock-connector/evaluate")

    assert response.status_code == 403
    assert response.json()["detail"] == "Valid X-API-Key header required for this premium endpoint"


def test_premium_connector_evaluate_rejects_invalid_api_key(client):
    response = client.post(
        "/api/v2/connectors/mock-connector/evaluate",
        headers={"X-API-Key": "not-a-real-key"},
    )

    assert response.status_code == 403


def test_premium_connector_evaluate_accepts_active_api_key_before_route_logic(client, db_session):
    db_session.add(ApiKey(key="bg_live_test", plan="premium", is_active=True, project_id=1))
    db_session.commit()

    response = client.post(
        "/api/v2/connectors/mock-connector/evaluate",
        headers={"X-API-Key": "bg_live_test"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Connector not found"
