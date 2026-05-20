from app.connector_config import ConnectorConfig
from app.services import alert_service
from app.services.listener_service import process_connector_event


def auth_headers(client, email="alert-owner@example.com"):
    password = "StrongPass123!"
    register = client.post(
        "/api/v2/auth/register",
        json={"email": email, "password": password, "project_name": "Alert Project"},
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


def test_alert_rule_crud_and_test_notification(client, monkeypatch):
    monkeypatch.setattr("app.services.alert_service.test_alert_rule", lambda rule: True)
    headers = auth_headers(client)
    project_id = first_project_id(client, headers)

    created = client.post(
        f"/api/v2/projects/{project_id}/alerts",
        headers=headers,
        json={
            "condition": "decision_not_allow",
            "channel_type": "webhook",
            "config": {"url": "https://alerts.example.test/bridgeguard"},
        },
    )
    assert created.status_code == 201
    alert = created.json()
    assert alert["condition"] == "decision_not_allow"

    listed = client.get(f"/api/v2/projects/{project_id}/alerts", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.put(
        f"/api/v2/projects/{project_id}/alerts/{alert['id']}",
        headers=headers,
        json={"condition": "risk_score_gt", "threshold": 70.0, "is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["threshold"] == 70.0
    assert updated.json()["is_active"] is False

    tested = client.post(
        f"/api/v2/projects/{project_id}/alerts/{alert['id']}/test",
        headers=headers,
    )
    assert tested.status_code == 200
    assert tested.json() == {"sent": True, "channel_type": "webhook"}

    deleted = client.delete(
        f"/api/v2/projects/{project_id}/alerts/{alert['id']}",
        headers=headers,
    )
    assert deleted.status_code == 200
    assert client.get(
        f"/api/v2/projects/{project_id}/alerts/{alert['id']}",
        headers=headers,
    ).status_code == 404


def test_listener_decision_dispatches_matching_alert_rule(client, db_session, monkeypatch):
    sent_payloads = []
    monkeypatch.setattr(
        "app.services.listener_service.queue_decision_notification",
        lambda decision_id: None,
    )
    monkeypatch.setitem(
        alert_service.NOTIFIERS,
        "webhook",
        lambda config, payload: sent_payloads.append((config, payload)) or True,
    )
    headers = auth_headers(client, "dispatch-owner@example.com")
    project_id = first_project_id(client, headers)

    created = client.post(
        f"/api/v2/projects/{project_id}/alerts",
        headers=headers,
            json={
                "condition": "risk_score_gt",
                "threshold": 50.0,
                "channel_type": "webhook",
                "config": {"url": "https://alerts.example.test/bridgeguard"},
            },
    )
    assert created.status_code == 201

    record = process_connector_event(
        db=db_session,
        project_id=project_id,
        connector_config=ConnectorConfig(
            id="alert-dispatch-mock",
            name="Alert Dispatch Mock",
            rpc_url="mock://bridge",
            chain_id=1,
            contract_address="0x0000000000000000000000000000000000000000",
        ),
        event={
            "amount": 100.0,
            "locked_collateral": 100.0,
            "minted_supply": 200.0,
            "burned_proven": 100.0,
            "released_supply": 100.0,
            "total_inflow": 100.0,
            "total_outflow": 200.0,
            "current_block": 100,
            "tx_block": 90,
        },
    )

    assert alert_service.dispatch_alerts_for_decision(db_session, record.id) == 1
    assert sent_payloads[0][0]["url"] == "https://alerts.example.test/bridgeguard"
    assert sent_payloads[0][1]["decision"] == "FREEZE"
    assert sent_payloads[0][1]["decision_id"] == record.id
