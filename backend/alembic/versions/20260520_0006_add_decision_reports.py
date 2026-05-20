"""add decision reports

Revision ID: 20260520_0006
Revises: 20260520_0005
Create Date: 2026-05-20 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260520_0006"
down_revision: Union[str, None] = "20260520_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "decision_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("decision_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("signature", sa.String(length=128), nullable=False),
        sa.Column("signature_algorithm", sa.String(length=64), nullable=False),
        sa.Column("report_sha256", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["decision_id"], ["decision_records.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_decision_reports_decision_id"), "decision_reports", ["decision_id"], unique=False)
    op.create_index(op.f("ix_decision_reports_id"), "decision_reports", ["id"], unique=False)
    op.create_index(op.f("ix_decision_reports_project_id"), "decision_reports", ["project_id"], unique=False)
    op.create_index(op.f("ix_decision_reports_signature"), "decision_reports", ["signature"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_decision_reports_signature"), table_name="decision_reports")
    op.drop_index(op.f("ix_decision_reports_project_id"), table_name="decision_reports")
    op.drop_index(op.f("ix_decision_reports_id"), table_name="decision_reports")
    op.drop_index(op.f("ix_decision_reports_decision_id"), table_name="decision_reports")
    op.drop_table("decision_reports")
