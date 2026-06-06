"""Therapeutic-relations module: ergo ↔ patient links (cloisonnement backbone).

An ergothérapeute manages their own relations; admins may view all (aggregated
oversight). A relation grants the ergo access to that patient's data elsewhere.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_ergo
from app.db.session import get_db
from app.models.relation import RelationTherapeutique
from app.models.user import User, UserRole
from app.schemas.relation import RelationCreate, RelationRead

router = APIRouter()


@router.post("", response_model=RelationRead, status_code=status.HTTP_201_CREATED)
def create_relation(
    payload: RelationCreate,
    db: Session = Depends(get_db),
    ergo: User = Depends(require_ergo),
):
    patient = db.get(User, payload.patient_id)
    if patient is None or patient.role != UserRole.PATIENT:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing = db.scalar(
        select(RelationTherapeutique).where(
            RelationTherapeutique.ergo_id == ergo.id,
            RelationTherapeutique.patient_id == patient.id,
        )
    )
    if existing:
        existing.active = True
        db.commit()
        db.refresh(existing)
        return existing

    rel = RelationTherapeutique(ergo_id=ergo.id, patient_id=patient.id)
    db.add(rel)
    db.commit()
    db.refresh(rel)
    return rel


@router.get("", response_model=list[RelationRead])
def my_relations(
    db: Session = Depends(get_db), ergo: User = Depends(require_ergo)
):
    return list(
        db.scalars(
            select(RelationTherapeutique).where(
                RelationTherapeutique.ergo_id == ergo.id
            )
        )
    )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def end_relation(
    patient_id: int,
    db: Session = Depends(get_db),
    ergo: User = Depends(require_ergo),
) -> None:
    """Deactivate (soft) the therapeutic relation — revokes data access."""
    rel = db.scalar(
        select(RelationTherapeutique).where(
            RelationTherapeutique.ergo_id == ergo.id,
            RelationTherapeutique.patient_id == patient_id,
        )
    )
    if rel is None:
        raise HTTPException(status_code=404, detail="Relation not found")
    rel.active = False
    db.commit()
