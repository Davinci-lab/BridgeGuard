import json
from pathlib import Path
from typing import Iterable

from .connector_config import ConnectorConfig
from .connectors import BaseConnector, CosmosConnector, EVMConnector, SolanaConnector


class ConnectorRegistry:
    _connectors: dict[str, type[BaseConnector]] = {
        EVMConnector.connector_type: EVMConnector,
        SolanaConnector.connector_type: SolanaConnector,
        CosmosConnector.connector_type: CosmosConnector,
    }

    @classmethod
    def register(cls, connector_type: str, connector_cls: type[BaseConnector]) -> None:
        cls._connectors[connector_type] = connector_cls

    @classmethod
    def create(cls, config: ConnectorConfig) -> BaseConnector:
        connector_cls = cls._connectors.get(config.type)
        if connector_cls is None:
            raise ValueError(f"Unsupported connector type: {config.type}")
        return connector_cls(config)

    @classmethod
    def supported_types(cls) -> list[str]:
        return sorted(cls._connectors)

    @classmethod
    def discover_from_config_files(cls, files: Iterable[Path]) -> list[ConnectorConfig]:
        discovered: list[ConnectorConfig] = []
        seen: set[tuple[str, int, str, str]] = set()
        for path in files:
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            items = data if isinstance(data, list) else data.get("connectors", [])
            for item in items:
                try:
                    config = ConnectorConfig(**item)
                except Exception:
                    continue
                key = (
                    config.type,
                    config.chain_id,
                    config.contract_address.lower(),
                    config.name.lower(),
                )
                if key in seen:
                    continue
                discovered.append(config)
                seen.add(key)
        return discovered
