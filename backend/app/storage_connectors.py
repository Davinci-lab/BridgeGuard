import json
import os
from pathlib import Path
from typing import List
from .connector_config import ConnectorConfig

CONNECTORS_FILE = Path("connectors.json")

def load_connectors() -> List[ConnectorConfig]:
    if not CONNECTORS_FILE.exists():
        return []
    try:
        with open(CONNECTORS_FILE) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return []
    return [ConnectorConfig(**item) for item in data]

def save_connectors(connectors: List[ConnectorConfig]):
    temp_file = CONNECTORS_FILE.with_suffix(".json.tmp")
    with open(temp_file, "w") as f:
        json.dump([c.model_dump() for c in connectors], f, indent=2)
    os.replace(temp_file, CONNECTORS_FILE)

def get_connector(connector_id: str) -> ConnectorConfig:
    connectors = load_connectors()
    for c in connectors:
        if c.id == connector_id:
            return c
    raise KeyError(f"Connector {connector_id} not found")
