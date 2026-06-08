"""prescriptions + évaluation multi-axes + champs prescripteur/RPPS

Revision ID: 0003_presc_eval
Revises: 0002_search
Create Date: 2026-06-07
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_presc_eval"
down_revision: Union[str, None] = "0002_search"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_AXES = ("pertinence_clinique", "utilisabilite", "efficacite", "accessibilite", "integration")
_COMMENTS = ("avantages", "limites", "contexte_utilisation", "profil_patient")


def upgrade() -> None:
    # --- users : identité prescripteur + RPPS ---
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("etablissement", sa.String(255), nullable=True))
        batch.add_column(sa.Column("rpps", sa.String(20), nullable=True))
        batch.add_column(
            sa.Column("rpps_verified", sa.Boolean(), nullable=False, server_default=sa.false())
        )

    # --- evaluations : passage mono-note -> multi-axes ---
    with op.batch_alter_table("evaluations") as batch:
        for axe in _AXES:
            batch.add_column(sa.Column(axe, sa.Integer(), nullable=False, server_default="3"))
        for c in _COMMENTS:
            batch.add_column(sa.Column(c, sa.Text(), nullable=True))
        batch.drop_column("rating")
        batch.drop_column("comment")

    # --- prescriptions ---
    op.create_table(
        "prescriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ergo_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("share_token", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_prescriptions_ergo_id", "prescriptions", ["ergo_id"])
    op.create_index("ix_prescriptions_patient_id", "prescriptions", ["patient_id"])
    op.create_index("ix_prescriptions_share_token", "prescriptions", ["share_token"], unique=True)

    op.create_table(
        "prescription_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "prescription_id",
            sa.Integer(),
            sa.ForeignKey("prescriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "application_id",
            sa.Integer(),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("consignes", sa.Text(), nullable=True),
        sa.Column("priorite", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("feedback_patient", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_prescription_items_prescription_id", "prescription_items", ["prescription_id"]
    )


def downgrade() -> None:
    op.drop_table("prescription_items")
    op.drop_index("ix_prescriptions_share_token", table_name="prescriptions")
    op.drop_index("ix_prescriptions_patient_id", table_name="prescriptions")
    op.drop_index("ix_prescriptions_ergo_id", table_name="prescriptions")
    op.drop_table("prescriptions")

    with op.batch_alter_table("evaluations") as batch:
        batch.add_column(sa.Column("rating", sa.Integer(), nullable=False, server_default="3"))
        batch.add_column(sa.Column("comment", sa.Text(), nullable=True))
        for c in _COMMENTS:
            batch.drop_column(c)
        for axe in _AXES:
            batch.drop_column(axe)

    with op.batch_alter_table("users") as batch:
        batch.drop_column("rpps_verified")
        batch.drop_column("rpps")
        batch.drop_column("etablissement")
