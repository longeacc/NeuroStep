"""ORM models — import all so Base.metadata sees them."""

from app.models.user import User, UserRole
from app.models.cognition import (
    FonctionCognitive,
    RetentissementVieQuotidienne,
    SousFonction,
    trouble_retentissements,
    trouble_sous_fonctions,
)
from app.models.taxonomy import Trouble, Theme
from app.models.application import Application, application_themes, application_troubles
from app.models.evaluation import Evaluation
from app.models.relation import RelationTherapeutique
from app.models.prescription import (
    Prescription,
    PrescriptionAccessLog,
    PrescriptionItem,
)

__all__ = [
    "User",
    "UserRole",
    "FonctionCognitive",
    "SousFonction",
    "RetentissementVieQuotidienne",
    "trouble_sous_fonctions",
    "trouble_retentissements",
    "Trouble",
    "Theme",
    "Application",
    "application_troubles",
    "application_themes",
    "Evaluation",
    "RelationTherapeutique",
    "Prescription",
    "PrescriptionItem",
    "PrescriptionAccessLog",
]
