from app.attack_replay import load_attacks, attack_to_simulation, load_normal_flows
from app.policy_engine import decide
from app.models import PolicyDecision

def test_all_attacks_result_in_defensive_action():
    attacks = load_attacks()
    for attack in attacks:
        sim = attack_to_simulation(attack)
        decision, risk, reasons, _, _ = decide(sim)
        assert decision != PolicyDecision.ALLOW, f"{attack.name} should not be ALLOW"
        assert risk > 30, f"Risk too low for {attack.name}"

def test_all_attacks_match_expected_decision():
    attacks = load_attacks()
    for attack in attacks:
        sim = attack_to_simulation(attack)
        decision, _, _, _, _ = decide(sim)
        assert decision == attack.expected_decision, (
            f"{attack.name} expected {attack.expected_decision}, got {decision}"
        )

def test_normal_flows_are_allowed():
    normal = load_normal_flows()
    for sim in normal:
        decision, risk, reasons, _, _ = decide(sim)
        assert decision == PolicyDecision.ALLOW
