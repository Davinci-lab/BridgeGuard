"""add policy configs

Revision ID: 20260520_0005
Revises: 20260520_0004
Create Date: 2026-05-20 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260520_0005"
down_revision: Union[str, None] = "20260520_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "policy_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("risk_weights", sa.JSON(), nullable=False),
        sa.Column("custom_rules", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_policy_configs_id"), "policy_configs", ["id"], unique=False)
    op.create_index(
        op.f("ix_policy_configs_project_id"),
        "policy_configs",
        ["project_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_policy_configs_project_id"), table_name="policy_configs")
    op.drop_index(op.f("ix_policy_configs_id"), table_name="policy_configs")
    op.drop_table("policy_configs")
