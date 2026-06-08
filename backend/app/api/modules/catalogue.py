"""Catalogue module: applications/tools CRUD + filtered listing.

Public reads (Utilisateur perspective). Writes require admin (ADMIN perspective).
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.application import Application
from app.models.cognition import FonctionCognitive, RetentissementVieQuotidienne
from app.models.taxonomy import Theme, Trouble
from app.models.user import User
from app.schemas.catalogue import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
    FonctionCognitiveRead,
    RetentissementRead,
    ThemeRead,
    TroubleRead,
)
from app.services import catalogue as svc
from app.services import search as search_svc

router = APIRouter()


# --- Taxonomy helpers (sidebar in the prototype) ---
@router.get("/_meta/troubles", response_model=list[TroubleRead], tags=["catalogue"])
def list_troubles(db: Session = Depends(get_db)):
    return list(db.scalars(select(Trouble).order_by(Trouble.name)))


@router.get("/_meta/themes", response_model=list[ThemeRead], tags=["catalogue"])
def list_themes(db: Session = Depends(get_db)):
    return list(db.scalars(select(Theme).order_by(Theme.name)))


@router.get(
    "/_meta/fonctions", response_model=list[FonctionCognitiveRead], tags=["catalogue"]
)
def list_fonctions(db: Session = Depends(get_db)):
    """L'ADAPT cognitive functions + their sub-functions."""
    return list(db.scalars(select(FonctionCognitive).order_by(FonctionCognitive.nom)))


@router.get(
    "/_meta/retentissements",
    response_model=list[RetentissementRead],
    tags=["catalogue"],
)
def list_retentissements(db: Session = Depends(get_db)):
    """Retentissements en vie quotidienne (filtre de recherche enrichie)."""
    return list(
        db.scalars(
            select(RetentissementVieQuotidienne).order_by(
                RetentissementVieQuotidienne.libelle
            )
        )
    )


# --- Applications ---
@router.get("", response_model=list[ApplicationRead])
def list_apps(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, description="search name/description"),
    os: str | None = Query(default=None, description="platform filter, e.g. iOS"),
    trouble: str | None = Query(default=None, description="pathology filter"),
):
    return svc.list_applications(db, q=q, os=os, trouble=trouble)


# --- Recherche multi-critères enrichie (spec 5.3) ---
@router.get("/search", response_model=list[ApplicationRead], tags=["catalogue"])
def search_apps(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, description="recherche full-text FR"),
    fonction: str | None = Query(default=None, description="fonction cognitive L'ADAPT"),
    sous_fonction: str | None = Query(default=None, description="sous-fonction"),
    trouble: str | None = Query(default=None, description="trouble (pathologie)"),
    retentissement: str | None = Query(
        default=None, description="retentissement en vie quotidienne"
    ),
    plateformes: list[str] | None = Query(
        default=None, description="supports (répétable), ex: ?plateformes=Web&plateformes=iOS"
    ),
    gratuit: bool | None = Query(default=None, description="filtrer sur la gratuité"),
    objectif: str | None = Query(default=None, description="objectif thérapeutique"),
):
    return search_svc.search_applications(
        db,
        q=q,
        fonction=fonction,
        sous_fonction=sous_fonction,
        trouble=trouble,
        retentissement=retentissement,
        plateformes=plateformes,
        gratuit=gratuit,
        objectif=objectif,
    )


@router.get("/{app_id}", response_model=ApplicationRead)
def get_app(app_id: int, db: Session = Depends(get_db)):
    app = db.get(Application, app_id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.post(
    "", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED
)
def create_app(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    app = Application(
        nom=payload.nom,
        description=payload.description,
        objectif_ther=payload.objectif_ther,
        image=payload.image,
        url_store=payload.url_store,
        gratuit=payload.gratuit,
        enrichi=payload.enrichi,
        plateformes=payload.plateformes,
        troubles=svc.resolve_troubles(db, payload.troubles),
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.put("/{app_id}", response_model=ApplicationRead)
def update_app(
    app_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    app = db.get(Application, app_id)
    if app is None:
        raise HTTPException(status_code=404, detail="Application not found")

    data = payload.model_dump(exclude_unset=True)
    troubles = data.pop("troubles", None)
    for field, value in data.items():
        setattr(app, field, value)
    if troubles is not None:
        app.troubles = svc.resolve_troubles(db, troubles)

    db.commit()
    db.refresh(app)
    return app
