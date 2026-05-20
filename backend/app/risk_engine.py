from typing import List
from .reason_codes import ReasonCode

RISK_WEIGHTS = {
    ReasonCode.MINT_EXCEEDS_LOCKED: 35,
    ReasonCode.RELEASE_EXCEEDS_BURNED: 35,
    ReasonCode.OUTFLOW_EXCEEDS_INFLOW: 30,
    ReasonCode.EMERGENCY_MODE_ACTIVE: 100,  # immediately freeze
    ReasonCode.REPLAY_OR_DUPLICATE_MESSAGE: 90,
    ReasonCode.UNKNOWN_OR_CHANGED_ROOT: 80,
    ReasonCode.CONFIG_CHANGE_UNCOOLED: 70,
    ReasonCode.SIGNER_THRESHOLD_WEAK: 50,
    ReasonCode.VALIDATOR_SET_RISK: 60,
    ReasonCode.CHAIN_FINALITY_NOT_REACHED: 20,
    ReasonCode.ABNORMAL_VOLUME_SPIKE: 20,
    ReasonCode.ASSET_CAP_EXCEEDED: 25,
    ReasonCode.ROUTE_CAP_EXCEEDED: 25,
    ReasonCode.TVL_DIVERGENCE: 40,
    ReasonCode.CUSTOM: 30,
}

class RiskEngine:
    @staticmethod
    def compute_risk_score(
        violations: List[ReasonCode],
        risk_weights: dict | None = None,
    ) -> float:
        if not violations:
            return 0.0
        weights = RISK_WEIGHTS.copy()
        for key, value in (risk_weights or {}).items():
            try:
                reason = key if isinstance(key, ReasonCode) else ReasonCode(str(key))
            except ValueError:
                continue
            weights[reason] = float(value)
        # Use max weight as base, add combination penalty
        max_weight = max((weights.get(v, 10) for v in violations), default=10)
        # Combination: multiple critical violations increase score
        combo_penalty = min(len(violations) * 5, 40)
        score = min(max_weight + combo_penalty, 100)
        return score
