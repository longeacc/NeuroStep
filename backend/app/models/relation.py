"""Therapeutic relationship (ergothérapeute ↔ patient).

Backbone of medical-secret data partitioning (RGPD art. 9, Code de la santé
publique): an ergo only accesses data of patients with an *active* relation.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RelationTherapeutique(Base):
    __tablename__ = "relations_therapeutiques"
    __table_args__ = (
        UniqueConstraint("ergo_id", "patient_id", name="uq_ergo_patient"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ergo_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Relation ergo={self.ergo_id} patient={self.patient_id} active={self.active}>"
