"""Data migration / seed: legacy data/database.json -> relational DB.

Idempotent: matches applications by `nom`, troubles/themes by `name`.
Also creates the first admin user from settings.

Run:  python -m app.seed
"""

import json
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.data.ladapt import LADAPT_FONCTIONS, TROUBLE_MAPPING
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.application import Application
from app.models.cognition import FonctionCognitive, SousFonction
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
            is_verified=True,
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


def seed_ladapt(db: Session) -> None:
    """Build the L'ADAPT cognitive taxonomy and map troubles onto it (spec 4.5.2)."""
    # Functions + sub-functions (get-or-create, idempotent).
    sous_index: dict[tuple[str, str], SousFonction] = {}
    for fnom, meta in LADAPT_FONCTIONS.items():
        fonction = db.scalar(
            select(FonctionCognitive).where(FonctionCognitive.nom == fnom)
        )
        if fonction is None:
            fonction = FonctionCognitive(nom=fnom, is_motrice=meta["is_motrice"])
            db.add(fonction)
            db.flush()
        for sf_nom in meta["sous_fonctions"]:
            sf = db.scalar(
                select(SousFonction).where(
                    SousFonction.fonction_id == fonction.id, SousFonction.nom == sf_nom
                )
            )
            if sf is None:
                sf = SousFonction(fonction_id=fonction.id, nom=sf_nom)
                db.add(sf)
                db.flush()
            sous_index[(fnom, sf_nom)] = sf

    # Map each trouble -> function + sub-functions.
    mapped = 0
    for tname, (fnom, sf_names) in TROUBLE_MAPPING.items():
        trouble = db.scalar(select(Trouble).where(Trouble.name == tname))
        if trouble is None:  # trouble absent from legacy data — skip silently
            continue
        fonction = db.scalar(
            select(FonctionCognitive).where(FonctionCognitive.nom == fnom)
        )
        trouble.fonction_id = fonction.id
        trouble.sous_fonctions = [sous_index[(fnom, s)] for s in sf_names]
        mapped += 1
    print(
        f"  + L'ADAPT: {len(LADAPT_FONCTIONS)} fonctions, "
        f"{len(sous_index)} sous-fonctions, {mapped} troubles mappés"
    )


def validate_integrity(db: Session) -> None:
    """Referential-integrity / completeness checks (spec 4.5 step 6)."""
    n_apps = db.scalar(select(func.count()).select_from(Application))
    n_troubles = db.scalar(select(func.count()).select_from(Trouble))
    n_fonctions = db.scalar(select(func.count()).select_from(FonctionCognitive))
    unmapped = list(
        db.scalars(select(Trouble.name).where(Trouble.fonction_id.is_(None)))
    )
    print(
        f"  Validation: {n_apps} applications, {n_fonctions} domaines cognitifs, "
        f"{n_troubles} troubles"
    )
    if unmapped:
        print(f"  ! troubles non mappés vers L'ADAPT: {unmapped}")


def main() -> None:
    if engine.dialect.name == "postgresql":
        # Schema expected from Alembic: run `alembic upgrade head` first.
        print("Seeding data (schema managed by Alembic)...")
    else:
        print("Creating schema (SQLite dev)...")
        Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_admin(db)
        seed_from_legacy(db)
        seed_ladapt(db)
        db.commit()
        validate_integrity(db)
    print("Seed done.")


if __name__ == "__main__":
    main()
