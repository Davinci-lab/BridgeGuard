def auth_headers(client, email="sim-owner@example.com"):
    password = "StrongPass123!"
    register = client.post(
        "/api/v2/auth/register",
        json={"email": email, "password": password, "project_name": "Simulation Project"},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/v2/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def first_project_id(client, headers):
    response = client.get("/api/v2/projects", headers=headers)
    assert response.status_code == 200
    return response.json()[0]["id"]


def test_v2_simulation_is_saved_under_project(client):
    headers = auth_headers(client)
    project_id = first_project_id(client, headers)

    response = client.post(
        "/api/v2/simulate",
        headers={**headers, "X-Project-ID": str(project_id)},
        json={"amount": 10, "locked_collateral": 10000, "minted_supply": 9000},
    )

    assert response.status_code == 200
    decision = response.json()
    assert decision["project_id"] == project_id
    assert decision["decision"] == "ALLOW"

    decisions = client.get(
        f"/api/v2/decisions?project_id={project_id}",
        headers=headers,
    )

    assert decisions.status_code == 200
    body = decisions.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == decision["id"]


def test_v2_project_ownership_is_enforced(client):
    owner_headers = auth_headers(client, "owner@example.com")
    other_headers = auth_headers(client, "other@example.com")
    owner_project_id = first_project_id(client, owner_headers)

    response = client.post(
        "/api/v2/simulate",
        headers={**other_headers, "X-Project-ID": str(owner_project_id)},
        json={"amount": 10},
    )

    assert response.status_code == 404


def test_project_create_delete_and_decision_pagination(client):
    headers = auth_headers(client, "pager@example.com")

    created = client.post("/api/v2/projects", headers=headers, json={"name": "Pager Project"})
    assert created.status_code == 201
    project_id = created.json()["id"]

    for amount in [1, 2, 3]:
        response = client.post(
            f"/api/v2/simulate?project_id={project_id}",
            headers=headers,
            json={"amount": amount},
        )
        assert response.status_code == 200

    page = client.get(
        f"/api/v2/decisions?project_id={project_id}&limit=2&offset=1",
        headers=headers,
    )
    assert page.status_code == 200
    assert page.json()["total"] == 3
    assert len(page.json()["items"]) == 2

    deleted = client.delete(f"/api/v2/projects/{project_id}", headers=headers)
    assert deleted.status_code == 200

    missing = client.get(f"/api/v2/decisions?project_id={project_id}", headers=headers)
    assert missing.status_code == 404
