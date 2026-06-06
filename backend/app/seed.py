"""Data migration / seed: legacy data/database.json -> relational DB.

Idempotent: matches applications by `nom`, troubles/themes by `name`.
Also creates the first admin user from settings.

Run:  python -m app.seed
"""

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.application import Application
from app.models.taxonomy import Theme, Trouble
from app.models.user import User, UserRole

# Legacy JSON lives at repo_root/data/database.json (two levels up from backend/app).
LEGACY_JSON = Path(__file__).resolve().parents[2] / "data" / "database.json"


def _get_or_create_trouble(db: Session, name: str) -> Trouble:
    obj = db.scalar(select(Trouble).where(Trouble.name == name))
    if obj is None:
        obj = Trouble(name=name)
        db.add(obj)
        db.flush()
    return obj


def _get_or_create_theme(db: Session, name: str) -> None:
    if db.scalar(select(Theme).where(Theme.name == name)) is None:
        db.add(Theme(name=name))


def seed_admin(db: Session) -> None:
    if db.scalar(select(User).where(User.email == settings.FIRST_ADMIN_EMAIL)):
        return
    db.add(
        User(
            email=settings.FIRST_ADMIN_EMAIL,
            hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
            full_name="Neurostep Admin",
            role=UserRole.ADMIN,
        )
    )
    print(f"  + admin user {settings.FIRST_ADMIN_EMAIL}")


def seed_from_legacy(db: Session) -> None:
    if not LEGACY_JSON.exists():
        print(f"  ! legacy JSON not found at {LEGACY_JSON}, skipping catalogue import")
        return

    data = json.loads(LEGACY_JSON.read_text(encoding="utf-8"))

    for name in data.get("themes", []):
        _get_or_create_theme(db, name)
    for name in data.get("troubles", []):
        _get_or_create_trouble(db, name)
    db.flush()

    imported = 0
    for raw in data.get("applications", []):
        nom = raw.get("nom", "").strip()
        if not nom:
            continue
        if db.scalar(select(Application).where(Application.nom == nom)):
            continue  # idempotent
        app = Application(
            nom=nom,
            description=raw.get("description"),
            objectif_ther=raw.get("objectif_ther"),
            image=raw.get("image") or None,
            url_store=raw.get("url_store") or None,
            gratuit=bool(raw.get("gratuit", False)),
            enrichi=bool(raw.get("enrichi", False)),
            plateformes=raw.get("plateformes", []),
            troubles=[_get_or_create_trouble(db, t) for t in raw.get("troubles", [])],
        )
        db.add(app)
        imported += 1
    print(f"  + {imported} applications imported")


def main() -> None:
    print("Creating schema...")
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_admin(db)
        seed_from_legacy(db)
        db.commit()
    print("Seed done.")


if __name__ == "__main__":
    main()
