import json
import os

import httpx
from pydantic import BaseModel, Field

from ..connector_config import EVMMethodMapping


ETHERSCAN_API_URL = "https://api.etherscan.io/v2/api"
ETHERSCAN_API_KEYS = {
    1: "ETHERSCAN_API_KEY",
    11155111: "ETHERSCAN_API_KEY",
}


class ConnectorDiscoveryRequest(BaseModel):
    chain_id: int = 1
    contract_address: str
    api_key: str | None = None


class ConnectorDiscoveryResponse(BaseModel):
    contract_address: str
    chain_id: int
    verified: bool
    abi: list = Field(default_factory=list)
    method_mapping: EVMMethodMapping
    warning: str | None = None


METHOD_HINTS = {
    "locked_collateral": ["totallocked", "locked", "collateral", "outstandingbridged"],
    "minted_supply": ["totalminted", "minted", "totalsupply", "supply"],
    "burned_proven": ["totalburned", "burned", "burn"],
    "released_supply": ["totalreleased", "released", "release"],
    "signer_count": ["signercount", "numguardians", "guardians", "validators"],
    "required_signers": ["requiredsigners", "threshold", "required"],
    "emergency_mode": ["emergency", "paused", "shutdown"],
    "config_change_block": ["configchangeblock", "lastconfigblock"],
    "current_block": ["currentblock", "blocknumber"],
}


def suggest_method_mapping(abi: list) -> EVMMethodMapping:
    function_names = [
        item.get("name", "")
        for item in abi
        if item.get("type") == "function"
        and item.get("stateMutability") in {"view", "pure"}
        and not item.get("inputs")
    ]
    normalized = {name.lower(): name for name in function_names}
    suggestion: dict[str, str | None] = {}
    for field, hints in METHOD_HINTS.items():
        suggestion[field] = None
        if field in {"locked_collateral", "minted_supply", "burned_proven", "released_supply"}:
            suggestion[field] = ""
        for normalized_name, original_name in normalized.items():
            if any(hint in normalized_name for hint in hints):
                suggestion[field] = original_name
                break
    return EVMMethodMapping(**suggestion)


def discover_evm_connector(request: ConnectorDiscoveryRequest) -> ConnectorDiscoveryResponse:
    api_key = request.api_key or os.getenv(ETHERSCAN_API_KEYS.get(request.chain_id, "ETHERSCAN_API_KEY"), "")
    if not api_key:
        return ConnectorDiscoveryResponse(
            contract_address=request.contract_address,
            chain_id=request.chain_id,
            verified=False,
            method_mapping=EVMMethodMapping(),
            warning="ETHERSCAN_API_KEY is not configured",
        )

    response = httpx.get(
        ETHERSCAN_API_URL,
        params={
            "module": "contract",
            "action": "getabi",
            "chainid": request.chain_id,
            "address": request.contract_address,
            "apikey": api_key,
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != "1":
        return ConnectorDiscoveryResponse(
            contract_address=request.contract_address,
            chain_id=request.chain_id,
            verified=False,
            method_mapping=EVMMethodMapping(),
            warning=payload.get("result") or "ABI is not verified",
        )

    abi = json.loads(payload["result"])
    return ConnectorDiscoveryResponse(
        contract_address=request.contract_address,
        chain_id=request.chain_id,
        verified=True,
        abi=abi,
        method_mapping=suggest_method_mapping(abi),
    )
