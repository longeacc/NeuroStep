"""Module évaluations multi-axes (spec 5.5).

Notation 5 axes (1..5) + commentaires structurés, par des professionnels.
La valeur différenciante vient d'auteurs identifiés (RPPS vérifié).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_ergo
from app.db.session import get_db
from app.models.application import Application
from app.models.evaluation import AXES, Evaluation
from app.models.user import User
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationRead,
    EvaluationSummary,
)

router = APIRouter()


def _to_read(ev: Evaluation, author: User | None) -> EvaluationRead:
    read = EvaluationRead.model_validate(ev)
    read.auteur_rpps_verifie = bool(author and author.rpps_verified)
    return read


@router.post("", response_model=EvaluationRead, status_code=status.HTTP_201_CREATED)
def create_evaluation(
    payload: EvaluationCreate,
    db: Session = Depends(get_db),
    ergo: User = Depends(require_ergo),
):
    if db.get(Application, payload.application_id) is None:
        raise HTTPException(status_code=404, detail="Application introuvable")
    ev = Evaluation(user_id=ergo.id, **payload.model_dump())
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return _to_read(ev, ergo)


@router.get("/application/{app_id}", response_model=list[EvaluationRead])
def list_for_app(app_id: int, db: Session = Depends(get_db)):
    evals = list(db.scalars(select(Evaluation).where(Evaluation.application_id == app_id)))
    authors = {
        u.id: u
        for u in db.scalars(
            select(User).where(User.id.in_([e.user_id for e in evals] or [0]))
        )
    }
    return [_to_read(e, authors.get(e.user_id)) for e in evals]


@router.get("/application/{app_id}/summary", response_model=EvaluationSummary)
def summary_for_app(app_id: int, db: Session = Depends(get_db)):
    cols = [func.avg(getattr(Evaluation, a)) for a in AXES]
    row = db.execute(
        select(func.count(Evaluation.id), *cols).where(
            Evaluation.application_id == app_id
        )
    ).one()
    nombre = row[0]
    par_axe = {
        axe: round(float(val), 2)
        for axe, val in zip(AXES, row[1:])
        if val is not None
    }
    moyenne_globale = (
        round(sum(par_axe.values()) / len(par_axe), 2) if par_axe else None
    )
    return EvaluationSummary(
        application_id=app_id,
        nombre=nombre,
        moyenne_globale=moyenne_globale,
        moyennes_par_axe=par_axe,
    )
