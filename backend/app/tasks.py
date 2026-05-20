import os

from celery import Celery


celery_app = Celery(
    "bridgeguard",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
)


@celery_app.task(name="bridgeguard.run_listener")
def run_listener(listener_id: int) -> str:
    from .services.listener_service import run_listener_once

    return run_listener_once(listener_id)


@celery_app.task(name="bridgeguard.send_decision_notification")
def send_decision_notification(decision_id: str) -> str:
    from .database import SessionLocal
    from .services.alert_service import dispatch_alerts_for_decision

    db = SessionLocal()
    try:
        sent = dispatch_alerts_for_decision(db, decision_id)
        return f"sent {sent} alert notifications"
    finally:
        db.close()
