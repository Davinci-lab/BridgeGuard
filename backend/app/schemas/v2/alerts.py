from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


AlertCondition = Literal["decision_not_allow", "risk_score_gt"]
AlertChannel = Literal["slack", "email", "webhook"]


class AlertRuleBase(BaseModel):
    condition: AlertCondition
    threshold: float | None = Field(default=None, ge=0)
    channel_type: AlertChannel
    config: dict
    is_active: bool = True

    @model_validator(mode="after")
    def validate_condition(self):
        if self.condition == "risk_score_gt" and self.threshold is None:
            raise ValueError("threshold is required for risk_score_gt")
        return self


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    condition: AlertCondition | None = None
    threshold: float | None = Field(default=None, ge=0)
    channel_type: AlertChannel | None = None
    config: dict | None = None
    is_active: bool | None = None


class AlertRuleRead(AlertRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime


class AlertTestResponse(BaseModel):
    sent: bool
    channel_type: AlertChannel
