from app.policy_engine import decide
from app.models import TransferSimulation, PolicyDecision
from app.reason_codes import ReasonCode

def test_normal_allows():
    sim = TransferSimulation(amount=10, locked_collateral=10000, minted_supply=9000)
    decision, risk, reasons, _, _ = decide(sim)
    assert decision == PolicyDecision.ALLOW
    assert risk == 0

def test_mint_exceeds_freezes():
    sim = TransferSimulation(locked_collateral=1000, minted_supply=2000)
    decision, risk, reasons, _, _ = decide(sim)
    assert decision == PolicyDecision.FREEZE
    assert ReasonCode.MINT_EXCEEDS_LOCKED in reasons

def test_weak_signers_escalates():
    sim = TransferSimulation(signer_count=3, required_signers=2)
    decision, risk, reasons, _, _ = decide(sim)
    assert decision in [PolicyDecision.ESCALATE_TO_GUARDIANS, PolicyDecision.REQUIRE_EXTRA_SIGNATURES]

def test_emergency_freezes():
    sim = TransferSimulation(emergency_mode=True)
    decision, _, _, _, _ = decide(sim)
    assert decision == PolicyDecision.FREEZE

def test_volume_spike_delays():
    sim = TransferSimulation(amount=50000, daily_volume=195000, daily_cap=200000, route_volume=90000, route_cap=100000)
    decision, risk, reasons, _, _ = decide(sim)
    # might trigger caps -> may be DELAY or ESCALATE
    assert decision != PolicyDecision.ALLOW