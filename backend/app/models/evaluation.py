"""Évaluation multi-axes d'un outil par un professionnel (spec 5.5).

5 axes notés 1–5 (pertinence clinique, utilisabilité, efficacité, accessibilité,
intégration) + commentaires structurés. La crédibilité vient de l'auteur :
ergothérapeute à RPPS vérifié (cf. User.rpps_verified).
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

# Axes de notation (1..5), utilisés pour la moyenne agrégée.
AXES = (
    "pertinence_clinique",
    "utilisabilite",
    "efficacite",
    "accessibilite",
    "integration",
)


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # --- Notes par axe (1..5) ---
    pertinence_clinique: Mapped[int] = mapped_column(Integer)
    utilisabilite: Mapped[int] = mapped_column(Integer)
    efficacite: Mapped[int] = mapped_column(Integer)
    accessibilite: Mapped[int] = mapped_column(Integer)
    integration: Mapped[int] = mapped_column(Integer)

    # --- Commentaires structurés ---
    avantages: Mapped[str | None] = mapped_column(Text, default=None)
    limites: Mapped[str | None] = mapped_column(Text, default=None)
    contexte_utilisation: Mapped[str | None] = mapped_column(Text, default=None)
    profil_patient: Mapped[str | None] = mapped_column(Text, default=None)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    @property
    def moyenne(self) -> float:
        return round(
            sum(getattr(self, a) for a in AXES) / len(AXES), 2
        )
