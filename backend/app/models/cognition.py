"""L'ADAPT cognitive taxonomy.

Cognitive functions (domaines) → sub-functions (sous-fonctions), plus daily-life
impacts (retentissements en vie quotidienne). A `Trouble` (legacy pathology label)
maps to one function and one-or-more sub-functions per spec 4.5.2.

"Compensation motrice" is included (Hémiplégie) though motor, not cognitive —
flagged via `is_motrice`.
"""

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Trouble <-> SousFonction (M:N): e.g. Aphasie -> Production + Réception.
trouble_sous_fonctions = Table(
    "trouble_sous_fonctions",
    Base.metadata,
    Column("trouble_id", ForeignKey("troubles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "sous_fonction_id",
        ForeignKey("sous_fonctions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# Trouble <-> Retentissement (M:N): daily-life impacts of a trouble.
trouble_retentissements = Table(
    "trouble_retentissements",
    Base.metadata,
    Column("trouble_id", ForeignKey("troubles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "retentissement_id",
        ForeignKey("retentissements.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class FonctionCognitive(Base):
    __tablename__ = "fonctions_cognitives"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # True for "Compensation motrice" (motor, kept for tools compensating motor deficits).
    is_motrice: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    sous_fonctions: Mapped[list["SousFonction"]] = relationship(
        back_populates="fonction", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FonctionCognitive {self.nom}>"


class SousFonction(Base):
    __tablename__ = "sous_fonctions"
    __table_args__ = (
        UniqueConstraint("fonction_id", "nom", name="uq_sousfonction_nom"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fonction_id: Mapped[int] = mapped_column(
        ForeignKey("fonctions_cognitives.id", ondelete="CASCADE"), index=True
    )
    nom: Mapped[str] = mapped_column(String(255))

    fonction: Mapped[FonctionCognitive] = relationship(back_populates="sous_fonctions")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SousFonction {self.nom}>"


class RetentissementVieQuotidienne(Base):
    __tablename__ = "retentissements"

    id: Mapped[int] = mapped_column(primary_key=True)
    libelle: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Retentissement {self.libelle}>"
