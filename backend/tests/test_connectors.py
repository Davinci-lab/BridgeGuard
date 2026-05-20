from app.connector_config import ConnectorConfig
from app.connector_registry import ConnectorRegistry
from app.connectors import ConnectorEngine
from app.services.connector_discovery import suggest_method_mapping


def create_premium_api_key(client, email="demo@bridgeguard.local"):
    password = "StrongPass123!"
    register = client.post(
        "/api/v2/auth/register",
        json={"email": email, "password": password, "project_name": "Premium Project"},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/v2/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    projects = client.get("/api/v2/projects", headers=headers)
    assert projects.status_code == 200
    project_id = projects.json()[0]["id"]

    key_response = client.post(
        "/api/v2/api-keys",
        headers=headers,
        json={"project_id": project_id, "plan": "premium"},
    )
    assert key_response.status_code == 201
    return key_response.json()["key"]


def test_connector_engine_returns_decision_without_live_chain(monkeypatch):
    monkeypatch.setattr("app.connectors.WEB3_AVAILABLE", False)
    config = ConnectorConfig(
        id="mock-connector",
        name="Mock EVM Bridge",
        rpc_url="http://localhost:8545",
        chain_id=1,
        contract_address="0x0000000000000000000000000000000000000000",
    )

    result = ConnectorEngine.evaluate(config)

    assert "decision" in result
    assert "risk_score" in result
    assert "reason_codes" in result


def test_connector_engine_supports_solana_and_cosmos_mocks():
    for connector_type in ["solana", "cosmos"]:
        config = ConnectorConfig(
            id=f"mock-{connector_type}",
            name=f"Mock {connector_type}",
            type=connector_type,
            rpc_url="mock://local",
            chain_id=1,
            contract_address="mock-address",
        )

        result = ConnectorEngine.evaluate(config)

        assert result["simulation"]["source_chain"] == config.source_chain
        assert "decision" in result
        assert "risk_score" in result
        assert connector_type.capitalize() in result["warning"]


def test_connector_registry_discovers_default_config_file():
    from pathlib import Path

    configs = ConnectorRegistry.discover_from_config_files(
        [Path("app/sample_data/default_connectors.json")]
    )

    assert configs
    assert all(config.type in ConnectorRegistry.supported_types() for config in configs)


def test_discovery_suggests_method_mapping_from_abi():
    abi = [
        {"type": "function", "stateMutability": "view", "name": "totalLocked", "inputs": []},
        {"type": "function", "stateMutability": "view", "name": "totalSupply", "inputs": []},
        {"type": "function", "stateMutability": "view", "name": "emergencyShutdown", "inputs": []},
    ]

    mapping = suggest_method_mapping(abi)

    assert mapping.locked_collateral == "totalLocked"
    assert mapping.minted_supply == "totalSupply"
    assert mapping.emergency_mode == "emergencyShutdown"


def test_v2_connector_discovery_endpoint(client, monkeypatch):
    api_key = create_premium_api_key(client)

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "1",
                "result": (
                    '[{"type":"function","stateMutability":"view","name":"totalLocked","inputs":[]},'
                    '{"type":"function","stateMutability":"view","name":"totalSupply","inputs":[]}]'
                ),
            }

    monkeypatch.setattr("app.services.connector_discovery.httpx.get", lambda *args, **kwargs: FakeResponse())

    response = client.post(
        "/api/v2/connectors/discover",
        headers={"X-API-Key": api_key},
        json={
            "chain_id": 1,
            "contract_address": "0x0000000000000000000000000000000000000000",
            "api_key": "test-key",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["verified"] is True
    assert body["method_mapping"]["locked_collateral"] == "totalLocked"
