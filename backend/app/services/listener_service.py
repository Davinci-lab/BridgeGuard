from datetime import datetime, timezone
import logging
import os
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..connector_config import ConnectorConfig
from ..connectors import ConnectorEngine
from ..models import TransferSimulation
from ..models.auth_models import Project
from ..models.decision_models import DecisionRecord as DBDecisionRecord
from ..models.listener_models import Listener
from ..policy_engine import decide
from .policy_service import get_effective_policy


logger = logging.getLogger(__name__)


def save_simulation_decision(
    db: Session,
    project_id: int,
    simulation: TransferSimulation,
    enqueue_notifications: bool = False,
) -> DBDecisionRecord:
    policy = get_effective_policy(db, project_id)
    decision, risk_score, violations, explanation, recommended = decide(
        simulation,
        risk_weights=policy["risk_weights"],
        custom_rules=policy["custom_rules"],
    )
    record = DBDecisionRecord(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        simulation=simulation.model_dump(mode="json"),
        decision=decision.value,
        risk_score=risk_score,
        reason_codes=[reason.value for reason in violations],
        explanation=explanation,
        recommended_action=recommended,
        project_id=project_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    if enqueue_notifications:
        queue_decision_notification(record.id)

    return record


def queue_decision_notification(decision_id: str) -> None:
    from ..tasks import send_decision_notification

    try:
        send_decision_notification.delay(decision_id)
    except Exception:
        logger.exception("Failed to enqueue decision notification for %s", decision_id)


def event_to_simulation(config: ConnectorConfig, event: dict) -> TransferSimulation:
    defaults = {
        "source_chain": config.source_chain,
        "dest_chain": config.dest_chain,
        "asset": config.asset,
        "daily_cap": config.daily_cap,
        "route_cap": config.route_cap,
        "asset_cap": config.asset_cap,
        "finality_blocks": config.finality_blocks,
    }
    return TransferSimulation(**{**defaults, **event})


def process_connector_event(
    db: Session,
    project_id: int,
    connector_config: ConnectorConfig,
    event: dict,
) -> DBDecisionRecord:
    simulation = event_to_simulation(connector_config, event)
    return save_simulation_decision(db, project_id, simulation, enqueue_notifications=True)


def poll_connector_once(
    db: Session,
    project_id: int,
    connector_config: ConnectorConfig,
) -> DBDecisionRecord:
    result = ConnectorEngine.evaluate(connector_config)
    simulation = TransferSimulation(**result["simulation"])
    return save_simulation_decision(db, project_id, simulation, enqueue_notifications=True)


def start_listener(
    db: Session,
    project: Project,
    connector_config: ConnectorConfig,
    mode: str = "polling",
) -> Listener:
    now = datetime.now(timezone.utc)
    listener = db.scalar(
        select(Listener).where(
            Listener.project_id == project.id,
            Listener.connector_id == connector_config.id,
        )
    )
    if listener is None:
        listener = Listener(
            project_id=project.id,
            connector_id=connector_config.id,
            connector_config=connector_config.model_dump(mode="json"),
            status="starting",
            mode=mode,
            created_at=now,
            updated_at=now,
        )
        db.add(listener)
    else:
        listener.connector_config = connector_config.model_dump(mode="json")
        listener.status = "starting"
        listener.mode = mode
        listener.last_error = None
        listener.updated_at = now

    db.commit()
    db.refresh(listener)

    from ..tasks import run_listener

    task = run_listener.delay(listener.id)
    listener.task_id = task.id
    listener.status = "running"
    listener.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(listener)
    return listener


def stop_listener(db: Session, project: Project, connector_id: str | None = None) -> list[Listener]:
    query = select(Listener).where(Listener.project_id == project.id)
    if connector_id:
        query = query.where(Listener.connector_id == connector_id)

    listeners = db.scalars(query).all()
    now = datetime.now(timezone.utc)
    for listener in listeners:
        listener.status = "stopped"
        listener.updated_at = now
    db.commit()
    return listeners


def run_listener_once(listener_id: int) -> str:
    from ..database import SessionLocal

    db = SessionLocal()
    try:
        listener = db.get(Listener, listener_id)
        if listener is None:
            return "listener not found"
        if listener.status == "stopped":
            return "listener stopped"

        config = ConnectorConfig(**listener.connector_config)
        poll_connector_once(db, listener.project_id, config)
        listener.status = "running"
        listener.last_error = None
        listener.updated_at = datetime.now(timezone.utc)
        db.commit()

        if listener.mode in {"polling", "websocket"}:
            from ..tasks import run_listener

            run_listener.apply_async(
                args=[listener.id],
                countdown=int(os.getenv("LISTENER_POLL_SECONDS", "30")),
            )
        return "processed"
    except Exception as exc:
        logger.exception("Listener %s failed", listener_id)
        listener = db.get(Listener, listener_id)
        if listener is not None:
            listener.status = "error"
            listener.last_error = str(exc)
            listener.updated_at = datetime.now(timezone.utc)
            db.commit()
        raise
    finally:
        db.close()


def log_decision_notification(decision_id: str) -> str:
    logger.warning("Decision %s requires operator notification", decision_id)
    return decision_id
