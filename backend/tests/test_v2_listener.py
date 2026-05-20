from app.connector_config import ConnectorConfig
from app.models.auth_models import Project
from app.models.decision_models import DecisionRecord
from app.models.listener_models import Listener
from app.services.listener_service import process_connector_event


def auth_headers(client, email="listener-owner@example.com"):
    password = "StrongPass123!"
    register = client.post(
        "/api/v2/auth/register",
        json={"email": email, "password": password, "project_name": "Listener Project"},
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


def mock_connector():
    return ConnectorConfig(
        id="mock-listener",
        name="Mock Listener Bridge",
        rpc_url="mock://bridge",
        chain_id=1,
        contract_address="0x0000000000000000000000000000000000000000",
    )


def test_listener_start_stop_endpoints(client, monkeypatch):
    class FakeTask:
        id = "task-123"

    monkeypatch.setattr("app.tasks.run_listener.delay", lambda listener_id: FakeTask())
    headers = auth_headers(client)
    project_id = first_project_id(client, headers)

    start = client.post(
        f"/api/v2/projects/{project_id}/listeners/start",
        headers=headers,
        json={"connector": mock_connector().model_dump(mode="json"), "mode": "polling"},
    )

    assert start.status_code == 202
    listener = start.json()
    assert listener["status"] == "running"
    assert listener["task_id"] == "task-123"
    assert listener["connector_id"] == "mock-listener"

    stop = client.post(
        f"/api/v2/projects/{project_id}/listeners/stop",
        headers=headers,
        json={"connector_id": "mock-listener"},
    )

    assert stop.status_code == 200
    assert stop.json()[0]["status"] == "stopped"


def test_mock_listener_event_saves_project_decision_and_notifies(
    client,
    db_session,
    monkeypatch,
):
    notified = []
    monkeypatch.setattr(
        "app.services.listener_service.queue_decision_notification",
        lambda decision_id: notified.append(decision_id),
    )
    headers = auth_headers(client, "event-owner@example.com")
    project_id = first_project_id(client, headers)
    project = db_session.get(Project, project_id)
    assert project is not None

    record = process_connector_event(
        db=db_session,
        project_id=project.id,
        connector_config=mock_connector(),
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

    assert record.project_id == project_id
    assert record.decision == "FREEZE"
    assert notified == [record.id]

    saved = db_session.get(DecisionRecord, record.id)
    assert saved is not None
    assert saved.simulation["minted_supply"] == 200.0
    assert db_session.query(Listener).count() == 0
