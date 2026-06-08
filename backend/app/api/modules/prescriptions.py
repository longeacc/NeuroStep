"""Module prescription numérique (spec 5.4) + partage sécurisé (spec 5.6).

Workflow ergo : créer (brouillon) → valider → partager (lien signé / PDF) → révoquer.
Workflow patient : consulter via le lien (sans compte), donner un feedback d'usage.
Le lien est un JWT signé (HMAC-SHA256) avec jti (UUID v4) révocable et exp encodée ;
chaque accès est horodaté (log).
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import ensure_active_relation, get_current_user, require_ergo
from app.core.config import settings
from app.core.security import create_share_token, decode_share_token
from app.db.session import get_db
from app.models.prescription import (
    STATUS_DRAFT,
    STATUS_VALIDATED,
    Prescription,
    PrescriptionAccessLog,
    PrescriptionItem,
)
from app.models.user import User, UserRole
from app.schemas.prescription import (
    FeedbackCreate,
    PrescriptionCreate,
    PrescriptionRead,
    ValidateRequest,
)
from app.services.pdf import render_prescription_pdf

router = APIRouter()


def _share_jwt(presc: Prescription) -> str | None:
    """Recalcule le JWT de partage si le lien est actif (non révoqué, non expiré)."""
    if not presc.share_jti or presc.share_revoked or not presc.share_expires_at:
        return None
    exp = presc.share_expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp <= datetime.now(timezone.utc):
        return None
    return create_share_token(presc.id, presc.share_jti, exp)


def _to_read(presc: Prescription) -> PrescriptionRead:
    read = PrescriptionRead.model_validate(presc)
    read.share_token = _share_jwt(presc)
    return read


def _get_owned(db: Session, presc_id: int, user: User) -> Prescription:
    presc = db.get(Prescription, presc_id)
    if presc is None:
        raise HTTPException(status_code=404, detail="Prescription introuvable")
    if user.id not in (presc.ergo_id, presc.patient_id) and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return presc


def _resolve_shared(db: Session, token: str) -> Prescription:
    """Décode + valide un token de partage (signature, exp, jti, révocation)."""
    decoded = decode_share_token(token)
    if decoded is None:
        raise HTTPException(status_code=404, detail="Lien invalide ou expiré")
    presc_id, jti = decoded
    presc = db.get(Prescription, presc_id)
    if (
        presc is None
        or presc.status != STATUS_VALIDATED
        or presc.share_revoked
        or presc.share_jti != jti
    ):
        raise HTTPException(status_code=404, detail="Lien invalide ou révoqué")
    return presc


@router.post("", response_model=PrescriptionRead, status_code=status.HTTP_201_CREATED)
def create_prescription(
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    ergo: User = Depends(require_ergo),
):
    patient = db.get(User, payload.patient_id)
    if patient is None or patient.role != UserRole.PATIENT:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    ensure_active_relation(ergo, patient.id, db)  # cloisonnement

    presc = Prescription(
        ergo_id=ergo.id,
        patient_id=patient.id,
        status=STATUS_DRAFT,
        notes=payload.notes,
        items=[
            PrescriptionItem(
                application_id=i.application_id,
                consignes=i.consignes,
                priorite=i.priorite,
            )
            for i in payload.items
        ],
    )
    db.add(presc)
    db.commit()
    db.refresh(presc)
    return _to_read(presc)


@router.get("", response_model=list[PrescriptionRead])
def my_prescriptions(db: Session = Depends(get_db), ergo: User = Depends(require_ergo)):
    rows = db.scalars(select(Prescription).where(Prescription.ergo_id == ergo.id))
    return [_to_read(p) for p in rows]


@router.get("/{presc_id}", response_model=PrescriptionRead)
def get_prescription(
    presc_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return _to_read(_get_owned(db, presc_id, user))


@router.post("/{presc_id}/validate", response_model=PrescriptionRead)
def validate_prescription(
    presc_id: int,
    payload: ValidateRequest | None = None,
    db: Session = Depends(get_db),
    ergo: User = Depends(require_ergo),
):
    presc = db.get(Prescription, presc_id)
    if presc is None or presc.ergo_id != ergo.id:
        raise HTTPException(status_code=404, detail="Prescription introuvable")

    from datetime import timedelta

    days = (payload.expires_days if payload else None) or settings.SHARE_TOKEN_EXPIRE_DAYS
    days = max(settings.SHARE_TOKEN_MIN_DAYS, min(settings.SHARE_TOKEN_MAX_DAYS, days))

    presc.status = STATUS_VALIDATED
    presc.validated_at = datetime.now(timezone.utc)
    presc.share_jti = str(uuid.uuid4())
    presc.share_revoked = False
    presc.share_expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    db.commit()
    db.refresh(presc)
    return _to_read(presc)


@router.post("/{presc_id}/share/revoke", response_model=PrescriptionRead)
def revoke_share(
    presc_id: int, db: Session = Depends(get_db), ergo: User = Depends(require_ergo)
):
    presc = db.get(Prescription, presc_id)
    if presc is None or presc.ergo_id != ergo.id:
        raise HTTPException(status_code=404, detail="Prescription introuvable")
    presc.share_revoked = True
    db.commit()
    db.refresh(presc)
    return _to_read(presc)


@router.get("/{presc_id}/pdf")
def prescription_pdf(
    presc_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    presc = _get_owned(db, presc_id, user)
    if presc.status != STATUS_VALIDATED:
        raise HTTPException(status_code=409, detail="Prescription non validée")
    ergo = db.get(User, presc.ergo_id)
    pdf = render_prescription_pdf(presc, ergo, share_token=_share_jwt(presc))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="prescription-{presc.id}.pdf"'},
    )


# --- Accès patient via lien sécurisé (sans authentification) ---
@router.get("/shared/{token}", response_model=PrescriptionRead, tags=["prescriptions"])
def shared_prescription(token: str, request: Request, db: Session = Depends(get_db)):
    presc = _resolve_shared(db, token)
    # Log d'accès horodaté (spec 5.6).
    db.add(
        PrescriptionAccessLog(
            prescription_id=presc.id,
            ip=request.client.host if request.client else None,
        )
    )
    db.commit()
    return _to_read(presc)


@router.post("/shared/{token}/items/{item_id}/feedback", status_code=status.HTTP_200_OK)
def submit_feedback(
    token: str, item_id: int, payload: FeedbackCreate, db: Session = Depends(get_db)
):
    presc = _resolve_shared(db, token)
    item = db.get(PrescriptionItem, item_id)
    if item is None or item.prescription_id != presc.id:
        raise HTTPException(status_code=404, detail="Outil introuvable")
    item.feedback_patient = payload.feedback
    db.commit()
    return {"status": "ok"}
