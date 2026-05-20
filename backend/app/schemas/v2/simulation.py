from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ...models import PolicyDecision, TransferSimulation
from ...reason_codes import ReasonCode


class DecisionRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    simulation: TransferSimulation
    decision: PolicyDecision
    risk_score: float
    reason_codes: list[ReasonCode]
    explanation: str
    recommended_action: str
    project_id: int


class PaginatedDecisions(BaseModel):
    items: list[DecisionRecordRead]
    total: int
    limit: int
    offset: int
