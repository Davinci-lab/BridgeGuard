"""add listeners

Revision ID: 20260520_0003
Revises: 20260520_0002
Create Date: 2026-05-20 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260520_0003"
down_revision: Union[str, None] = "20260520_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "listeners",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("connector_id", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("task_id", sa.String(length=255), nullable=True),
        sa.Column("connector_config", sa.JSON(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_listeners_connector_id"), "listeners", ["connector_id"], unique=False)
    op.create_index(op.f("ix_listeners_id"), "listeners", ["id"], unique=False)
    op.create_index(op.f("ix_listeners_project_id"), "listeners", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_listeners_project_id"), table_name="listeners")
    op.drop_index(op.f("ix_listeners_id"), table_name="listeners")
    op.drop_index(op.f("ix_listeners_connector_id"), table_name="listeners")
    op.drop_table("listeners")
