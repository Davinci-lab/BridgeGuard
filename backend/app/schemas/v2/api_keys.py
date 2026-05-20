from pydantic import BaseModel, ConfigDict, Field


class ApiKeyCreate(BaseModel):
    project_id: int
    plan: str = Field(default="premium", min_length=1, max_length=64)


class ApiKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    plan: str
    is_active: bool
    project_id: int
