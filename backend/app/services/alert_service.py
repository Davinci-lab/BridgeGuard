from datetime import datetime, timezone
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.alert_models import AlertRule
from ..models.decision_models import DecisionRecord
from .notifiers import email, slack, webhook


logger = logging.getLogger(__name__)

NOTIFIERS = {
    "email": email.send,
    "slack": slack.send,
    "webhook": webhook.send,
}


def rule_matches(rule: AlertRule, decision: DecisionRecord) -> bool:
    if rule.condition == "decision_not_allow":
        return decision.decision != "ALLOW"
    if rule.condition == "risk_score_gt":
        return decision.risk_score > float(rule.threshold or 0)
    return False


def build_alert_payload(rule: AlertRule, decision: DecisionRecord) -> dict:
    message = (
        f"BridgeGuard alert: decision {decision.decision} "
        f"with risk score {decision.risk_score:.0f} for project {decision.project_id}."
    )
    return {
        "message": message,
        "rule_id": rule.id,
        "project_id": decision.project_id,
        "decision_id": decision.id,
        "decision": decision.decision,
        "risk_score": decision.risk_score,
        "reason_codes": decision.reason_codes,
        "timestamp": decision.timestamp.isoformat(),
    }


def send_alert(rule: AlertRule, decision: DecisionRecord) -> bool:
    sender = NOTIFIERS.get(rule.channel_type)
    if sender is None:
        raise ValueError(f"Unsupported alert channel: {rule.channel_type}")
    return sender(rule.config, build_alert_payload(rule, decision))


def dispatch_alerts_for_decision(db: Session, decision_id: str) -> int:
    decision = db.get(DecisionRecord, decision_id)
    if decision is None:
        logger.warning("Decision %s not found for alert dispatch", decision_id)
        return 0

    rules = db.scalars(
        select(AlertRule).where(
            AlertRule.project_id == decision.project_id,
            AlertRule.is_active.is_(True),
        )
    ).all()
    sent = 0
    for rule in rules:
        if not rule_matches(rule, decision):
            continue
        send_alert(rule, decision)
        sent += 1
    return sent


def test_alert_rule(rule: AlertRule) -> bool:
    now = datetime.now(timezone.utc)
    fake_decision = DecisionRecord(
        id="test-notification",
        timestamp=now,
        simulation={},
        decision="ESCALATE_TO_GUARDIANS",
        risk_score=max(float(rule.threshold or 0) + 1, 75),
        reason_codes=["TEST_NOTIFICATION"],
        explanation="Test notification",
        recommended_action="No action required.",
        project_id=rule.project_id,
    )
    return send_alert(rule, fake_decision)
