"""Moteur de recherche multi-critères enrichi (spec 5.3, Fonctionnalité 1).

Recherche croisée par : texte (full-text FR), fonction cognitive L'ADAPT,
sous-fonction, trouble, retentissement en vie quotidienne, plateforme, gratuité,
objectif thérapeutique.

Dialect-aware : PostgreSQL utilise `to_tsvector('french', f_unaccent(...))` +
`plainto_tsquery` avec tri par `ts_rank` (l'index GIN `idx_app_search` couvre la
même expression). SQLite (dev) retombe sur un `ILIKE` portable.
"""

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.cognition import (
    FonctionCognitive,
    RetentissementVieQuotidienne,
    SousFonction,
)
from app.models.taxonomy import Trouble


def _pg_haystack():
    """Expression identique à celle de l'index `idx_app_search` (sinon l'index
    n'est pas utilisé). coalesce + concat `||`, le tout passé dans f_unaccent."""
    return func.f_unaccent(
        func.coalesce(Application.nom, "")
        .concat(" ")
        .concat(func.coalesce(Application.description, ""))
        .concat(" ")
        .concat(func.coalesce(Application.objectif_ther, ""))
    )


def search_applications(
    db: Session,
    *,
    q: str | None = None,
    fonction: str | None = None,
    sous_fonction: str | None = None,
    trouble: str | None = None,
    retentissement: str | None = None,
    plateformes: list[str] | None = None,
    gratuit: bool | None = None,
    objectif: str | None = None,
) -> list[Application]:
    is_pg = db.bind.dialect.name == "postgresql"
    stmt = select(Application)
    rank = None

    # --- texte : full-text FR (PG) / ILIKE (SQLite) ---
    if q:
        if is_pg:
            tsq = func.plainto_tsquery("french", func.f_unaccent(q))
            tsv = func.to_tsvector("french", _pg_haystack())
            stmt = stmt.where(tsv.op("@@")(tsq))
            rank = func.ts_rank(tsv, tsq)
        else:
            like = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    Application.nom.ilike(like),
                    Application.description.ilike(like),
                    Application.objectif_ther.ilike(like),
                )
            )

    # --- taxonomie L'ADAPT ---
    if fonction:
        stmt = stmt.where(
            Application.troubles.any(
                Trouble.fonction.has(FonctionCognitive.nom == fonction)
            )
        )
    if sous_fonction:
        stmt = stmt.where(
            Application.troubles.any(
                Trouble.sous_fonctions.any(SousFonction.nom == sous_fonction)
            )
        )
    if trouble:
        stmt = stmt.where(Application.troubles.any(Trouble.name == trouble))
    if retentissement:
        stmt = stmt.where(
            Application.troubles.any(
                Trouble.retentissements.any(
                    RetentissementVieQuotidienne.libelle == retentissement
                )
            )
        )

    # --- attributs simples ---
    if gratuit is not None:
        stmt = stmt.where(Application.gratuit.is_(gratuit))
    if objectif:
        stmt = stmt.where(Application.objectif_ther.ilike(f"%{objectif.lower()}%"))

    if rank is not None:
        stmt = stmt.order_by(rank.desc())

    apps = list(db.scalars(stmt).unique())

    # plateformes : intersection (overlap) — en Python pour rester portable jsonb/SQLite.
    if plateformes:
        wanted = set(plateformes)
        apps = [a for a in apps if wanted & set(a.plateformes or [])]
    return apps
