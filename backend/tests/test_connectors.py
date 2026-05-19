from app.connector_config import ConnectorConfig
from app.connectors import ConnectorEngine


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
