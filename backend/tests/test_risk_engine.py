from app.risk_engine import RiskEngine
from app.reason_codes import ReasonCode

def test_no_violations_zero():
    assert RiskEngine.compute_risk_score([]) == 0

def test_high_severity_gives_high_score():
    score = RiskEngine.compute_risk_score([ReasonCode.MINT_EXCEEDS_LOCKED, ReasonCode.REPLAY_OR_DUPLICATE_MESSAGE])
    assert score >= 80

def test_emergency_mode_max():
    score = RiskEngine.compute_risk_score([ReasonCode.EMERGENCY_MODE_ACTIVE])
    assert score == 100