"""Module prescription numérique (spec 5.4).

Workflow ergo : créer (brouillon) → valider → partager (lien sécurisé / PDF).
Workflow patient : consulter via le lien, donner un feedback d'usage.
Cloisonnement : relation thérapeutique active requise côté ergo ; le patient
n'accède qu'à ses propres prescriptions.
"""

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import ensure_active_relation, get_current_user, require_ergo
from app.db.session import get_db
from app.models.prescription import (
    STATUS_DRAFT,
    STATUS_VALIDATED,
    Prescription,
    PrescriptionItem,
)
from app.models.user import User, UserRole
from app.schemas.prescription import (
    FeedbackCreate,
    PrescriptionCreate,
    PrescriptionRead,
)
from app.services.pdf import render_prescription_pdf

router = APIRouter()


def _get_owned(db: Session, presc_id: int, user: User) -> Prescription:
    """Charge une prescription accessible par `user` (ergo prescripteur ou patient)."""
    presc = db.get(Prescription, presc_id)
    if presc is None:
        raise HTTPException(status_code=404, detail="Prescription introuvable")
    if user.id not in (presc.ergo_id, presc.patient_id) and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Accès refusé")
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
    # Cloisonnement : relation thérapeutique active obligatoire.
    ensure_active_relation(ergo, patient.id, db)

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
    return presc


@router.get("", response_model=list[PrescriptionRead])
def my_prescriptions(db: Session = Depends(get_db), ergo: User = Depends(require_ergo)):
    return list(
        db.scalars(select(Prescription).where(Prescription.ergo_id == ergo.id))
    )


@router.get("/{presc_id}", response_model=PrescriptionRead)
def get_prescription(
    presc_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return _get_owned(db, presc_id, user)


@router.post("/{presc_id}/validate", response_model=PrescriptionRead)
def validate_prescription(
    presc_id: int, db: Session = Depends(get_db), ergo: User = Depends(require_ergo)
):
    presc = db.get(Prescription, presc_id)
    if presc is None or presc.ergo_id != ergo.id:
        raise HTTPException(status_code=404, detail="Prescription introuvable")
    presc.status = STATUS_VALIDATED
    presc.validated_at = datetime.now(timezone.utc)
    if not presc.share_token:
        presc.share_token = secrets.token_urlsafe(24)
    db.commit()
    db.refresh(presc)
    return presc


@router.get("/{presc_id}/pdf")
def prescription_pdf(
    presc_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    presc = _get_owned(db, presc_id, user)
    if presc.status != STATUS_VALIDATED:
        raise HTTPException(status_code=409, detail="Prescription non validée")
    ergo = db.get(User, presc.ergo_id)
    pdf = render_prescription_pdf(presc, ergo)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="prescription-{presc.id}.pdf"'
        },
    )


# --- Accès patient via lien sécurisé (sans authentification) ---
@router.get("/shared/{token}", response_model=PrescriptionRead, tags=["prescriptions"])
def shared_prescription(token: str, db: Session = Depends(get_db)):
    presc = db.scalar(select(Prescription).where(Prescription.share_token == token))
    if presc is None or presc.status != STATUS_VALIDATED:
        raise HTTPException(status_code=404, detail="Lien invalide")
    return presc


@router.post("/shared/{token}/items/{item_id}/feedback", status_code=status.HTTP_200_OK)
def submit_feedback(
    token: str, item_id: int, payload: FeedbackCreate, db: Session = Depends(get_db)
):
    """Le patient fournit un feedback d'usage sur un outil de sa prescription."""
    presc = db.scalar(select(Prescription).where(Prescription.share_token == token))
    if presc is None or presc.status != STATUS_VALIDATED:
        raise HTTPException(status_code=404, detail="Lien invalide")
    item = db.get(PrescriptionItem, item_id)
    if item is None or item.prescription_id != presc.id:
        raise HTTPException(status_code=404, detail="Outil introuvable")
    item.feedback_patient = payload.feedback
    db.commit()
    return {"status": "ok"}
