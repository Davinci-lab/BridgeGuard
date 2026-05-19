from app.invariant_engine import InvariantEngine
from app.models import TransferSimulation
from app.reason_codes import ReasonCode

def test_normal_transfer_no_violations():
    sim = TransferSimulation(
        source_chain="eth", dest_chain="arb", asset="USDC", amount=1000,
        locked_collateral=100000, minted_supply=90000,
        burned_proven=10000, released_supply=10000,
        total_inflow=90000, total_outflow=80000,
        daily_volume=5000, daily_cap=100000,
        route_volume=2000, route_cap=50000,
        asset_cap=500000,
        signer_count=10, required_signers=5,
        current_block=50, tx_block=40, finality_blocks=10,
        is_duplicate=False, emergency_mode=False, config_change_cooled=True
    )
    violations = InvariantEngine.check_invariants(sim)
    assert len(violations) == 0

def test_mint_exceeds_locked():
    sim = TransferSimulation(locked_collateral=100, minted_supply=200)
    violations = InvariantEngine.check_invariants(sim)
    assert ReasonCode.MINT_EXCEEDS_LOCKED in violations

def test_replay_detected():
    sim = TransferSimulation(is_duplicate=True)
    violations = InvariantEngine.check_invariants(sim)
    assert ReasonCode.REPLAY_OR_DUPLICATE_MESSAGE in violations

def test_emergency_mode():
    sim = TransferSimulation(emergency_mode=True)
    violations = InvariantEngine.check_invariants(sim)
    assert ReasonCode.EMERGENCY_MODE_ACTIVE in violations

def test_finality_not_reached():
    sim = TransferSimulation(current_block=20, tx_block=15, finality_blocks=10)
    violations = InvariantEngine.check_invariants(sim)
    assert ReasonCode.CHAIN_FINALITY_NOT_REACHED in violations

def test_config_uncooled():
    sim = TransferSimulation(config_change_cooled=False)
    violations = InvariantEngine.check_invariants(sim)
    assert ReasonCode.CONFIG_CHANGE_UNCOOLED in violations