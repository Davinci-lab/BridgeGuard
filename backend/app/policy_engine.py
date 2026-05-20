from typing import List, Tuple
from .reason_codes import ReasonCode
from .models import PolicyDecision, TransferSimulation
from .invariant_engine import InvariantEngine
from .risk_engine import RiskEngine

def decide(
    sim: TransferSimulation,
    risk_weights: dict | None = None,
    custom_rules: list[dict] | None = None,
) -> Tuple[PolicyDecision, float, List[ReasonCode], str, str]:
    violations = InvariantEngine.check_invariants(sim, custom_rules=custom_rules)
    risk_score = RiskEngine.compute_risk_score(violations, risk_weights=risk_weights)

    # Automatic freeze triggers
    if ReasonCode.MINT_EXCEEDS_LOCKED in violations or \
       ReasonCode.EMERGENCY_MODE_ACTIVE in violations or \
       ReasonCode.REPLAY_OR_DUPLICATE_MESSAGE in violations or \
       risk_score >= 85:
        decision = PolicyDecision.FREEZE
    elif risk_score >= 60:
        decision = PolicyDecision.ESCALATE_TO_GUARDIANS
    elif risk_score >= 30:
        if ReasonCode.SIGNER_THRESHOLD_WEAK in violations or \
           ReasonCode.CHAIN_FINALITY_NOT_REACHED in violations:
            decision = PolicyDecision.REQUIRE_EXTRA_SIGNATURES
        else:
            decision = PolicyDecision.DELAY
    else:
        decision = PolicyDecision.ALLOW

    # Build explanation
    if not violations:
        explanation = "All invariants satisfied, transfer appears safe."
        recommended = "Proceed normally."
    else:
        reasons_str = ", ".join(v.value for v in violations)
        explanation = f"Violations detected: {reasons_str}."
        recommended = {
            PolicyDecision.FREEZE: "Pause bridge route, require guardian review, rotate signers if needed.",
            PolicyDecision.ESCALATE_TO_GUARDIANS: "Escalate to governance guardians for manual inspection.",
            PolicyDecision.REQUIRE_EXTRA_SIGNATURES: "Require additional validator signatures before finalisation.",
            PolicyDecision.DELAY: "Hold transfer until cooldown/finality conditions are met.",
            PolicyDecision.ALLOW: "No action needed."
        }.get(decision, "Investigate further.")

    return decision, risk_score, violations, explanation, recommended
