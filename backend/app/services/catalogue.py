"""Catalogue service layer: query/filter + trouble resolution.

Reproduces the Streamlit prototype's filtering (search text, OS, trouble),
plus get-or-create of Trouble rows from free-text names.
"""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.taxonomy import Trouble


def resolve_troubles(db: Session, names: list[str]) -> list[Trouble]:
    """Get-or-create Trouble rows for the given names."""
    result: list[Trouble] = []
    for raw in names:
        name = raw.strip()
        if not name:
            continue
        trouble = db.scalar(select(Trouble).where(Trouble.name == name))
        if trouble is None:
            trouble = Trouble(name=name)
            db.add(trouble)
            db.flush()
        result.append(trouble)
    return result


def list_applications(
    db: Session,
    *,
    q: str | None = None,
    os: str | None = None,
    trouble: str | None = None,
) -> list[Application]:
    stmt = select(Application)

    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                Application.nom.ilike(like),
                Application.description.ilike(like),
            )
        )
    if trouble:
        stmt = stmt.where(Application.troubles.any(Trouble.name == trouble))

    apps = list(db.scalars(stmt).unique())

    # plateformes is a JSON array -> filter in Python (portable across backends).
    if os:
        apps = [a for a in apps if os in (a.plateformes or [])]
    return apps
