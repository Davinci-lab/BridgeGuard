from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
from .reason_codes import ReasonCode

class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    DELAY = "DELAY"
    FREEZE = "FREEZE"
    ESCALATE_TO_GUARDIANS = "ESCALATE_TO_GUARDIANS"
    REQUIRE_EXTRA_SIGNATURES = "REQUIRE_EXTRA_SIGNATURES"

class TransferSimulation(BaseModel):
    """Input for a simulated cross-chain transfer."""
    source_chain: str = "Ethereum"
    dest_chain: str = "Arbitrum"
    asset: str = "ETH"
    amount: float = 100.0
    signer_count: int = 10
    required_signers: int = 5
    finality_blocks: int = 10
    current_block: int = 10
    tx_block: int = 0
    is_duplicate: bool = False
    emergency_mode: bool = False
    config_change_cooled: bool = True
    locked_collateral: float = 10_000.0
    minted_supply: float = 9_000.0
    burned_proven: float = 1_000.0
    released_supply: float = 1_000.0
    daily_volume: float = 1_000.0
    daily_cap: float = 200_000.0
    route_volume: float = 1_000.0
    route_cap: float = 100_000.0
    asset_cap: float = 500_000.0
    total_inflow: float = 9_000.0
    total_outflow: float = 8_000.0
    known_message_hash: Optional[str] = None

class DecisionRecord(BaseModel):
    id: str
    timestamp: datetime
    simulation: TransferSimulation
    decision: PolicyDecision
    risk_score: float
    reason_codes: List[ReasonCode]
    explanation: str
    recommended_action: str

class Attack(BaseModel):
    name: str
    date: str
    loss: str
    bridge_type: str
    root_cause_category: str
    violated_invariant: str
    defensive_control: str
    expected_decision: PolicyDecision
    reason_codes: List[ReasonCode]
    summary: str
    source: Optional[str] = None

class Metrics(BaseModel):
    total_simulations: int
    risk_score_distribution: dict
    decisions_distribution: dict
    top_reason_codes: List[dict]
