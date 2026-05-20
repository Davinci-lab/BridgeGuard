from pydantic import BaseModel, ConfigDict


class ReportVerifyRequest(BaseModel):
    signature: str


class ReportVerifyResponse(BaseModel):
    valid: bool
    decision_id: str
    project_id: int


class DecisionReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    decision_id: str
    project_id: int
    signature: str
    signature_algorithm: str
    report_sha256: str
