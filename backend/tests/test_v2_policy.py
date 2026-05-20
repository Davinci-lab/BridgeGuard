def auth_headers(client, email="policy-owner@example.com"):
    password = "StrongPass123!"
    register = client.post(
        "/api/v2/auth/register",
        json={"email": email, "password": password, "project_name": "Policy Project"},
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


def test_custom_rule_triggers_reason_code(client):
    headers = auth_headers(client)
    project_id = first_project_id(client, headers)

    policy = client.put(
        f"/api/v2/projects/{project_id}/policy",
        headers=headers,
        json={
            "risk_weights": {},
            "custom_rules": [
                {
                    "name": "Large transfer",
                    "condition": "amount > 50",
                    "reason_code": "CUSTOM",
                }
            ],
        },
    )
    assert policy.status_code == 200
    assert policy.json()["custom_rules"][0]["name"] == "Large transfer"

    response = client.post(
        f"/api/v2/simulate?project_id={project_id}",
        headers=headers,
        json={"amount": 100},
    )

    assert response.status_code == 200
    body = response.json()
    assert "CUSTOM" in body["reason_codes"]
    assert body["decision"] == "DELAY"


def test_policy_risk_weight_override_changes_decision(client):
    headers = auth_headers(client, "weights-owner@example.com")
    project_id = first_project_id(client, headers)

    baseline = client.post(
        f"/api/v2/simulate?project_id={project_id}",
        headers=headers,
        json={"current_block": 20, "tx_block": 15, "finality_blocks": 10},
    )
    assert baseline.status_code == 200
    assert baseline.json()["decision"] == "ALLOW"
    assert baseline.json()["risk_score"] == 25

    policy = client.put(
        f"/api/v2/projects/{project_id}/policy",
        headers=headers,
        json={
            "risk_weights": {"CHAIN_FINALITY_NOT_REACHED": 70},
            "custom_rules": [],
        },
    )
    assert policy.status_code == 200
    assert policy.json()["risk_weights"]["CHAIN_FINALITY_NOT_REACHED"] == 70

    response = client.post(
        f"/api/v2/simulate?project_id={project_id}",
        headers=headers,
        json={"current_block": 20, "tx_block": 15, "finality_blocks": 10},
    )

    assert response.status_code == 200
    assert response.json()["risk_score"] == 75
    assert response.json()["decision"] == "ESCALATE_TO_GUARDIANS"


def test_get_policy_returns_defaults_when_unset(client):
    headers = auth_headers(client, "defaults-owner@example.com")
    project_id = first_project_id(client, headers)

    response = client.get(f"/api/v2/projects/{project_id}/policy", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["custom_rules"] == []
    assert body["risk_weights"]["MINT_EXCEEDS_LOCKED"] == 35
