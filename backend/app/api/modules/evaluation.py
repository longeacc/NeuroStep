"""Evaluation module — Phase 1 skeleton. Authenticated pros rate tools."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.application import Application
from app.models.evaluation import Evaluation
from app.models.user import User
from app.schemas.evaluation import EvaluationCreate, EvaluationRead

router = APIRouter()


@router.post("", response_model=EvaluationRead, status_code=status.HTTP_201_CREATED)
def create_evaluation(
    payload: EvaluationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if db.get(Application, payload.application_id) is None:
        raise HTTPException(status_code=404, detail="Application not found")
    ev = Evaluation(
        application_id=payload.application_id,
        user_id=user.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


@router.get("/application/{app_id}", response_model=list[EvaluationRead])
def list_for_app(app_id: int, db: Session = Depends(get_db)):
    return list(
        db.scalars(select(Evaluation).where(Evaluation.application_id == app_id))
    )
