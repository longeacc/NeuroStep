"""initial schema — users, taxonomy, applications, evaluations + FR search extensions

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# jsonb on PostgreSQL, plain JSON on SQLite (dev).
JSONType = sa.JSON().with_variant(JSONB, "postgresql")


def upgrade() -> None:
    bind = op.get_bind()
    is_pg = bind.dialect.name == "postgresql"

    # --- PostgreSQL search extensions (FR full-text + fuzzy + pgvector phase 2) ---
    if is_pg:
        op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
        op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        try:
            op.execute("CREATE EXTENSION IF NOT EXISTS vector")
        except Exception:  # pragma: no cover - pgvector optional in Phase 0
            pass

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "ERGO", "PATIENT", name="userrole"),
            nullable=False,
            server_default="ERGO",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "is_verified", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # --- L'ADAPT cognitive taxonomy (spec 4.5) ---
    op.create_table(
        "fonctions_cognitives",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(255), nullable=False),
        sa.Column(
            "is_motrice", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.create_index(
        "ix_fonctions_cognitives_nom", "fonctions_cognitives", ["nom"], unique=True
    )

    op.create_table(
        "sous_fonctions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "fonction_id",
            sa.Integer(),
            sa.ForeignKey("fonctions_cognitives.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("nom", sa.String(255), nullable=False),
        sa.UniqueConstraint("fonction_id", "nom", name="uq_sousfonction_nom"),
    )
    op.create_index("ix_sous_fonctions_fonction_id", "sous_fonctions", ["fonction_id"])

    op.create_table(
        "retentissements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("libelle", sa.String(512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_retentissements_libelle", "retentissements", ["libelle"], unique=True
    )

    # --- troubles / themes ---
    op.create_table(
        "troubles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "fonction_id",
            sa.Integer(),
            sa.ForeignKey("fonctions_cognitives.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_troubles_name", "troubles", ["name"], unique=True)

    op.create_table(
        "themes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
    )
    op.create_index("ix_themes_name", "themes", ["name"], unique=True)

    # --- applications ---
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("objectif_ther", sa.Text(), nullable=True),
        sa.Column("image", sa.String(1024), nullable=True),
        sa.Column("url_store", sa.String(1024), nullable=True),
        sa.Column("gratuit", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("enrichi", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("plateformes", JSONType, nullable=True),
    )
    op.create_index("ix_applications_nom", "applications", ["nom"])

    # --- association: application <-> trouble ---
    op.create_table(
        "application_troubles",
        sa.Column(
            "application_id",
            sa.Integer(),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "trouble_id",
            sa.Integer(),
            sa.ForeignKey("troubles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # --- association: application <-> theme ---
    op.create_table(
        "application_themes",
        sa.Column(
            "application_id",
            sa.Integer(),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "theme_id",
            sa.Integer(),
            sa.ForeignKey("themes.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # --- association: trouble <-> sous_fonction / retentissement (L'ADAPT) ---
    op.create_table(
        "trouble_sous_fonctions",
        sa.Column(
            "trouble_id",
            sa.Integer(),
            sa.ForeignKey("troubles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "sous_fonction_id",
            sa.Integer(),
            sa.ForeignKey("sous_fonctions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "trouble_retentissements",
        sa.Column(
            "trouble_id",
            sa.Integer(),
            sa.ForeignKey("troubles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "retentissement_id",
            sa.Integer(),
            sa.ForeignKey("retentissements.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # --- evaluations (Phase 1) ---
    op.create_table(
        "evaluations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "application_id",
            sa.Integer(),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_evaluations_application_id", "evaluations", ["application_id"])
    op.create_index("ix_evaluations_user_id", "evaluations", ["user_id"])

    # --- relations thérapeutiques (cloisonnement ergo <-> patient) ---
    op.create_table(
        "relations_therapeutiques",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "ergo_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "patient_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("ergo_id", "patient_id", name="uq_ergo_patient"),
    )
    op.create_index(
        "ix_relations_therapeutiques_ergo_id", "relations_therapeutiques", ["ergo_id"]
    )
    op.create_index(
        "ix_relations_therapeutiques_patient_id",
        "relations_therapeutiques",
        ["patient_id"],
    )

    # --- GIN trigram index on application name (typo-tolerant search, PG only) ---
    if is_pg:
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_applications_nom_trgm "
            "ON applications USING gin (nom gin_trgm_ops)"
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_pg = bind.dialect.name == "postgresql"

    if is_pg:
        op.execute("DROP INDEX IF EXISTS ix_applications_nom_trgm")

    op.drop_index(
        "ix_relations_therapeutiques_patient_id",
        table_name="relations_therapeutiques",
    )
    op.drop_index(
        "ix_relations_therapeutiques_ergo_id", table_name="relations_therapeutiques"
    )
    op.drop_table("relations_therapeutiques")
    op.drop_index("ix_evaluations_user_id", table_name="evaluations")
    op.drop_index("ix_evaluations_application_id", table_name="evaluations")
    op.drop_table("evaluations")
    op.drop_table("trouble_retentissements")
    op.drop_table("trouble_sous_fonctions")
    op.drop_table("application_themes")
    op.drop_table("application_troubles")
    op.drop_index("ix_applications_nom", table_name="applications")
    op.drop_table("applications")
    op.drop_index("ix_themes_name", table_name="themes")
    op.drop_table("themes")
    op.drop_index("ix_troubles_name", table_name="troubles")
    op.drop_table("troubles")
    op.drop_index("ix_retentissements_libelle", table_name="retentissements")
    op.drop_table("retentissements")
    op.drop_index("ix_sous_fonctions_fonction_id", table_name="sous_fonctions")
    op.drop_table("sous_fonctions")
    op.drop_index(
        "ix_fonctions_cognitives_nom", table_name="fonctions_cognitives"
    )
    op.drop_table("fonctions_cognitives")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    if is_pg:
        op.execute("DROP TYPE IF EXISTS userrole")
