"""moteur de recherche enrichi : f_unaccent immutable + index GIN full-text FR

Revision ID: 0002_search
Revises: 0001_initial
Create Date: 2026-06-07

PostgreSQL uniquement (no-op sur SQLite dev). `unaccent` n'étant pas IMMUTABLE,
on l'enveloppe dans `f_unaccent` (wrapper immuable documenté) pour pouvoir bâtir
un index d'expression `to_tsvector('french', f_unaccent(...))`.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002_search"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Doit rester identique à app/services/search.py::_pg_haystack (sinon l'index est ignoré).
_HAYSTACK = (
    "f_unaccent("
    "coalesce(nom,'') || ' ' || coalesce(description,'') || ' ' || "
    "coalesce(objectif_ther,''))"
)


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    # Wrapper IMMUTABLE autour de unaccent (requis pour un index d'expression).
    op.execute(
        """
        CREATE OR REPLACE FUNCTION f_unaccent(text)
        RETURNS text AS $$
          SELECT public.unaccent('public.unaccent', $1)
        $$ LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT
        """
    )

    # Index full-text français (nom + description + objectif thérapeutique).
    op.execute(
        f"CREATE INDEX IF NOT EXISTS idx_app_search ON applications "
        f"USING GIN (to_tsvector('french', {_HAYSTACK}))"
    )

    # Index sur le tableau jsonb des plateformes (filtre support).
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_app_plateformes "
        "ON applications USING GIN (plateformes jsonb_path_ops)"
    )


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute("DROP INDEX IF EXISTS idx_app_plateformes")
    op.execute("DROP INDEX IF EXISTS idx_app_search")
    op.execute("DROP FUNCTION IF EXISTS f_unaccent(text)")
