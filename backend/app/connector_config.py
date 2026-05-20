from pydantic import BaseModel, Field
from typing import Optional, Literal

class EVMMethodMapping(BaseModel):
    locked_collateral: str = "totalLocked"
    minted_supply: str = "totalMinted"
    burned_proven: str = "totalBurned"
    released_supply: str = "totalReleased"
    signer_count: Optional[str] = None
    required_signers: Optional[str] = None
    emergency_mode: Optional[str] = None
    config_change_block: Optional[str] = None
    current_block: Optional[str] = None

class ConnectorConfig(BaseModel):
    id: str = ""
    name: str
    type: Literal["evm", "solana", "cosmos"] = "evm"
    enabled: bool = True
    rpc_url: str = "mock://local"
    chain_id: int = 1
    contract_address: str = ""
    abi: list = Field(default_factory=list)
    method_mapping: EVMMethodMapping = Field(default_factory=EVMMethodMapping)
    # Additional caps can be set manually
    daily_cap: float = 1000000.0
    route_cap: float = 500000.0
    asset_cap: float = 2000000.0
    source_chain: str = "Ethereum"
    dest_chain: str = "Arbitrum"
    asset: str = "ETH"
    finality_blocks: int = 10
