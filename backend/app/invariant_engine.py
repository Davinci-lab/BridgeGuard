from typing import List, Tuple
from .reason_codes import ReasonCode
from .models import TransferSimulation

BUFFER_RATIO = 0.05  # 5% buffer for normal fluctuations

class InvariantEngine:
    @staticmethod
    def check_invariants(sim: TransferSimulation) -> List[ReasonCode]:
        violations: List[ReasonCode] = []

        # Core accounting
        if sim.minted_supply > sim.locked_collateral:
            violations.append(ReasonCode.MINT_EXCEEDS_LOCKED)
        if sim.released_supply > sim.burned_proven:
            violations.append(ReasonCode.RELEASE_EXCEEDS_BURNED)
        if sim.total_outflow > sim.total_inflow * (1 + BUFFER_RATIO):
            violations.append(ReasonCode.OUTFLOW_EXCEEDS_INFLOW)

        # Caps
        if sim.daily_volume > sim.daily_cap:
            violations.append(ReasonCode.ABNORMAL_VOLUME_SPIKE)
        if sim.amount > sim.asset_cap:
            violations.append(ReasonCode.ASSET_CAP_EXCEEDED)
        if sim.route_volume + sim.amount > sim.route_cap:
            violations.append(ReasonCode.ROUTE_CAP_EXCEEDED)

        # Governance / configuration
        if not sim.config_change_cooled:
            violations.append(ReasonCode.CONFIG_CHANGE_UNCOOLED)
        if sim.signer_count < sim.required_signers * 2:  # e.g. threshold too close
            violations.append(ReasonCode.SIGNER_THRESHOLD_WEAK)
        # Simulate unknown root: if locked_collateral is zero or very low, flag
        if sim.locked_collateral <= 0:
            violations.append(ReasonCode.UNKNOWN_OR_CHANGED_ROOT)

        # Finality
        if sim.current_block - sim.tx_block < sim.finality_blocks:
            violations.append(ReasonCode.CHAIN_FINALITY_NOT_REACHED)

        # Replay
        if sim.is_duplicate or sim.known_message_hash:
            violations.append(ReasonCode.REPLAY_OR_DUPLICATE_MESSAGE)

        # Emergency
        if sim.emergency_mode:
            violations.append(ReasonCode.EMERGENCY_MODE_ACTIVE)

        # TVL divergence (simplified: compare locked vs expected)
        if abs(sim.locked_collateral - (sim.minted_supply + sim.burned_proven)) > sim.locked_collateral * 0.1:
            violations.append(ReasonCode.TVL_DIVERGENCE)

        # Validator set risk (simplified)
        if sim.signer_count < 4:
            violations.append(ReasonCode.VALIDATOR_SET_RISK)

        return violations