import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from .connector_config import ConnectorConfig
from .connectors import ConnectorEngine
from .storage_connectors import load_connectors, save_connectors, get_connector
import uuid

router = APIRouter(prefix="/connectors", tags=["connectors"])
DEFAULT_CONNECTORS_FILE = Path(__file__).parent / "sample_data" / "default_connectors.json"

@router.get("/")
def list_connectors():
    return load_connectors()

@router.get("/presets")
def list_connector_presets():
    with open(DEFAULT_CONNECTORS_FILE, encoding="utf-8") as f:
        return [ConnectorConfig(**item) for item in json.load(f)]

@router.post("/")
def create_connector(config: ConnectorConfig):
    config.id = str(uuid.uuid4())
    connectors = load_connectors()
    connectors.append(config)
    save_connectors(connectors)
    return config

@router.put("/{connector_id}")
def update_connector(connector_id: str, config: ConnectorConfig):
    connectors = load_connectors()
    for i, c in enumerate(connectors):
        if c.id == connector_id:
            config.id = connector_id
            connectors[i] = config
            save_connectors(connectors)
            return config
    raise HTTPException(404, "Connector not found")

@router.delete("/{connector_id}")
def delete_connector(connector_id: str):
    connectors = load_connectors()
    new_connectors = [c for c in connectors if c.id != connector_id]
    if len(new_connectors) == len(connectors):
        raise HTTPException(404, "Connector not found")
    save_connectors(new_connectors)
    return {"status": "deleted"}

@router.post("/{connector_id}/evaluate")
def evaluate_connector(connector_id: str):
    config = get_connector(connector_id)
    try:
        result = ConnectorEngine.evaluate(config)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))
