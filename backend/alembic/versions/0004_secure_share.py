"""partage sécurisé : jti/révocation/expiration + log d'accès (spec 5.6)

Revision ID: 0004_share
Revises: 0003_presc_eval
Create Date: 2026-06-08
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004_share"
down_revision: Union[str, None] = "0003_presc_eval"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_prescriptions_share_token", table_name="prescriptions")
    with op.batch_alter_table("prescriptions") as batch:
        batch.add_column(sa.Column("share_jti", sa.String(36), nullable=True))
        batch.add_column(
            sa.Column("share_revoked", sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch.add_column(sa.Column("share_expires_at", sa.DateTime(timezone=True), nullable=True))
        batch.drop_column("share_token")
    op.create_index("ix_prescriptions_share_jti", "prescriptions", ["share_jti"], unique=True)

    op.create_table(
        "prescription_access_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "prescription_id",
            sa.Integer(),
            sa.ForeignKey("prescriptions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("accessed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip", sa.String(64), nullable=True),
    )
    op.create_index(
        "ix_prescription_access_logs_prescription_id",
        "prescription_access_logs",
        ["prescription_id"],
    )


def downgrade() -> None:
    op.drop_table("prescription_access_logs")
    op.drop_index("ix_prescriptions_share_jti", table_name="prescriptions")
    with op.batch_alter_table("prescriptions") as batch:
        batch.add_column(sa.Column("share_token", sa.String(64), nullable=True))
        batch.drop_column("share_expires_at")
        batch.drop_column("share_revoked")
        batch.drop_column("share_jti")
    op.create_index(
        "ix_prescriptions_share_token", "prescriptions", ["share_token"], unique=True
    )
