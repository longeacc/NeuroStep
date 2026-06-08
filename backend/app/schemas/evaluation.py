"""Schemas d'évaluation multi-axes (spec 5.5)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluationCreate(BaseModel):
    application_id: int
    # 5 axes notés 1..5
    pertinence_clinique: int = Field(ge=1, le=5)
    utilisabilite: int = Field(ge=1, le=5)
    efficacite: int = Field(ge=1, le=5)
    accessibilite: int = Field(ge=1, le=5)
    integration: int = Field(ge=1, le=5)
    # Commentaires structurés
    avantages: str | None = None
    limites: str | None = None
    contexte_utilisation: str | None = None
    profil_patient: str | None = None


class EvaluationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    user_id: int
    pertinence_clinique: int
    utilisabilite: int
    efficacite: int
    accessibilite: int
    integration: int
    avantages: str | None
    limites: str | None
    contexte_utilisation: str | None
    profil_patient: str | None
    moyenne: float
    created_at: datetime
    # Crédibilité : l'auteur est-il un pro à RPPS vérifié ?
    auteur_rpps_verifie: bool = False


class EvaluationSummary(BaseModel):
    application_id: int
    nombre: int
    moyenne_globale: float | None
    moyennes_par_axe: dict[str, float]
