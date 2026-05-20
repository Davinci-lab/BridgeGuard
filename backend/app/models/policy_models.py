from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.database import Base


policy_json = JSON().with_variant(JSONB, "postgresql")


class PolicyConfig(Base):
    __tablename__ = "policy_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    risk_weights: Mapped[dict] = mapped_column(policy_json, nullable=False, default=dict)
    custom_rules: Mapped[list[dict]] = mapped_column(policy_json, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    project = relationship("Project", back_populates="policy_config")
