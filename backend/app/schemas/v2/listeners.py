from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ...connector_config import ConnectorConfig


class ListenerStartRequest(BaseModel):
    connector: ConnectorConfig
    mode: str = Field(default="polling", pattern="^(polling|websocket)$")


class ListenerStopRequest(BaseModel):
    connector_id: str | None = None


class ListenerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    connector_id: str
    status: str
    mode: str
    task_id: str | None
    connector_config: dict
    last_error: str | None
    created_at: datetime
    updated_at: datetime
