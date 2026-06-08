"""Prescription numérique (spec 5.4).

Un ergothérapeute associe 1..N outils du catalogue à un patient, avec des consignes
personnalisées et une priorité, puis valide et partage (lien sécurisé / PDF).
L'accès est cloisonné par la relation thérapeutique (cf. api/deps.ensure_active_relation).
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Statuts du cycle de vie.
STATUS_DRAFT = "draft"
STATUS_VALIDATED = "validated"


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    ergo_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default=STATUS_DRAFT, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    # Partage sécurisé (spec 5.6) : le token est un JWT signé ; on stocke ici le
    # jti (UUID v4) pour la révocation + la date d'expiration.
    share_jti: Mapped[str | None] = mapped_column(
        String(36), unique=True, index=True, default=None
    )
    share_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    share_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    validated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    items: Mapped[list["PrescriptionItem"]] = relationship(
        back_populates="prescription",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="PrescriptionItem.priorite",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Prescription {self.id} ergo={self.ergo_id} patient={self.patient_id} {self.status}>"


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    prescription_id: Mapped[int] = mapped_column(
        ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True
    )
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE")
    )
    consignes: Mapped[str | None] = mapped_column(Text, default=None)
    # 1 = priorité haute … 3 = basse.
    priorite: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    # Feedback d'usage fourni par le patient via le lien partagé.
    feedback_patient: Mapped[str | None] = mapped_column(Text, default=None)

    prescription: Mapped[Prescription] = relationship(back_populates="items")
    application = relationship("Application", lazy="selectin")


class PrescriptionAccessLog(Base):
    """Log d'accès horodaté au lien partagé (spec 5.6)."""

    __tablename__ = "prescription_access_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    prescription_id: Mapped[int] = mapped_column(
        ForeignKey("prescriptions.id", ondelete="CASCADE"), index=True
    )
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    ip: Mapped[str | None] = mapped_column(String(64), default=None)
