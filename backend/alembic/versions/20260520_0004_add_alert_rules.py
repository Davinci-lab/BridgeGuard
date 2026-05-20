"""add alert rules

Revision ID: 20260520_0004
Revises: 20260520_0003
Create Date: 2026-05-20 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260520_0004"
down_revision: Union[str, None] = "20260520_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("condition", sa.String(length=64), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=True),
        sa.Column("channel_type", sa.String(length=32), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alert_rules_id"), "alert_rules", ["id"], unique=False)
    op.create_index(op.f("ix_alert_rules_project_id"), "alert_rules", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_alert_rules_project_id"), table_name="alert_rules")
    op.drop_index(op.f("ix_alert_rules_id"), table_name="alert_rules")
    op.drop_table("alert_rules")
