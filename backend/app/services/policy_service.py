from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.policy_models import PolicyConfig
from ..risk_engine import RISK_WEIGHTS


DEFAULT_RISK_WEIGHTS = {reason.value: weight for reason, weight in RISK_WEIGHTS.items()}


def normalize_policy(policy: PolicyConfig | None, project_id: int) -> dict:
    return {
        "project_id": project_id,
        "risk_weights": {
            **DEFAULT_RISK_WEIGHTS,
            **((policy.risk_weights or {}) if policy else {}),
        },
        "custom_rules": (policy.custom_rules or []) if policy else [],
    }


def get_policy_config(db: Session, project_id: int) -> PolicyConfig | None:
    return (
        db.query(PolicyConfig)
        .filter(PolicyConfig.project_id == project_id)
        .one_or_none()
    )


def get_effective_policy(db: Session, project_id: int) -> dict:
    return normalize_policy(get_policy_config(db, project_id), project_id)


def upsert_policy_config(
    db: Session,
    project_id: int,
    risk_weights: dict,
    custom_rules: list[dict],
) -> PolicyConfig:
    now = datetime.now(timezone.utc)
    policy = get_policy_config(db, project_id)
    if policy is None:
        policy = PolicyConfig(
            project_id=project_id,
            risk_weights=risk_weights,
            custom_rules=custom_rules,
            created_at=now,
            updated_at=now,
        )
        db.add(policy)
    else:
        policy.risk_weights = risk_weights
        policy.custom_rules = custom_rules
        policy.updated_at = now
    db.commit()
    db.refresh(policy)
    return policy
