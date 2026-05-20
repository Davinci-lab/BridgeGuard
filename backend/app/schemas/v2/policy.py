from pydantic import BaseModel, Field


class CustomRule(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    condition: str = Field(..., min_length=1, max_length=500)
    reason_code: str = Field(default="CUSTOM", min_length=1, max_length=128)


class PolicyConfigRead(BaseModel):
    project_id: int
    risk_weights: dict[str, float]
    custom_rules: list[CustomRule]


class PolicyConfigUpdate(BaseModel):
    risk_weights: dict[str, float] = Field(default_factory=dict)
    custom_rules: list[CustomRule] = Field(default_factory=list)
