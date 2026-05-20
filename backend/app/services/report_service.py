from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
import hashlib
import hmac
import json
import os
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from sqlalchemy.orm import Session

from ..models.decision_models import DecisionRecord
from ..models.report_models import DecisionReport


SIGNATURE_ALGORITHM = "HMAC-SHA256"

REPORT_HTML_TEMPLATE = """
<html>
  <body>
    <h1>BridgeGuard Decision Report</h1>
    <p><strong>Decision ID:</strong> {decision_id}</p>
    <p><strong>Project ID:</strong> {project_id}</p>
    <p><strong>Decision:</strong> {decision}</p>
    <p><strong>Risk score:</strong> {risk_score}</p>
    <p><strong>Reason codes:</strong> {reason_codes}</p>
    <p><strong>Recommended action:</strong> {recommended_action}</p>
    <p><strong>Signature:</strong> {signature}</p>
  </body>
</html>
"""


@dataclass
class GeneratedReport:
    pdf_bytes: bytes
    metadata: DecisionReport


def canonical_decision_payload(decision: DecisionRecord) -> dict:
    return {
        "id": decision.id,
        "timestamp": decision.timestamp.isoformat(),
        "project_id": decision.project_id,
        "simulation": decision.simulation,
        "decision": decision.decision,
        "risk_score": decision.risk_score,
        "reason_codes": decision.reason_codes,
        "explanation": decision.explanation,
        "recommended_action": decision.recommended_action,
    }


def signing_key_for_project(project_id: int) -> bytes:
    master_secret = os.getenv("REPORT_SIGNING_SECRET") or os.getenv(
        "SECRET_KEY",
        "bridgeguard-dev-secret-change-me",
    )
    return hmac.new(
        master_secret.encode("utf-8"),
        f"project:{project_id}".encode("utf-8"),
        hashlib.sha256,
    ).digest()


def sign_decision(decision: DecisionRecord) -> str:
    payload = json.dumps(
        canonical_decision_payload(decision),
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hmac.new(signing_key_for_project(decision.project_id), payload, hashlib.sha256).hexdigest()


def verify_decision_signature(decision: DecisionRecord, signature: str) -> bool:
    return hmac.compare_digest(sign_decision(decision), signature)


def render_report_html(decision: DecisionRecord, signature: str) -> str:
    return REPORT_HTML_TEMPLATE.format(
        decision_id=escape(decision.id),
        project_id=decision.project_id,
        decision=escape(decision.decision),
        risk_score=f"{decision.risk_score:.2f}",
        reason_codes=escape(", ".join(decision.reason_codes)),
        recommended_action=escape(decision.recommended_action),
        signature=escape(signature),
    )


def generate_pdf(decision: DecisionRecord, signature: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title=f"BridgeGuard Report {decision.id}")
    styles = getSampleStyleSheet()
    story = [
        Paragraph("BridgeGuard Decision Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"<b>Decision ID:</b> {escape(decision.id)}", styles["BodyText"]),
        Paragraph(f"<b>Project ID:</b> {decision.project_id}", styles["BodyText"]),
        Paragraph(f"<b>Timestamp:</b> {escape(decision.timestamp.isoformat())}", styles["BodyText"]),
        Paragraph(f"<b>Decision:</b> {escape(decision.decision)}", styles["BodyText"]),
        Paragraph(f"<b>Risk score:</b> {decision.risk_score:.2f}", styles["BodyText"]),
        Paragraph(f"<b>Reason codes:</b> {escape(', '.join(decision.reason_codes))}", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph(f"<b>Explanation:</b> {escape(decision.explanation)}", styles["BodyText"]),
        Paragraph(f"<b>Recommended action:</b> {escape(decision.recommended_action)}", styles["BodyText"]),
        Spacer(1, 12),
        Paragraph(f"<b>Signature algorithm:</b> {SIGNATURE_ALGORITHM}", styles["BodyText"]),
        Paragraph(f"<b>Signature:</b> {escape(signature)}", styles["Code"]),
    ]
    doc.build(story)
    return buffer.getvalue()


def create_decision_report(db: Session, decision: DecisionRecord) -> GeneratedReport:
    signature = sign_decision(decision)
    pdf_bytes = generate_pdf(decision, signature)
    metadata = DecisionReport(
        decision_id=decision.id,
        project_id=decision.project_id,
        signature=signature,
        signature_algorithm=SIGNATURE_ALGORITHM,
        report_sha256=hashlib.sha256(pdf_bytes).hexdigest(),
        created_at=datetime.now(timezone.utc),
    )
    db.add(metadata)
    db.commit()
    db.refresh(metadata)
    return GeneratedReport(pdf_bytes=pdf_bytes, metadata=metadata)
