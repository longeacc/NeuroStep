"""Reference taxonomies: Trouble (pathology) and Theme (activity area).

A Trouble is mapped onto the L'ADAPT cognitive taxonomy (function + sub-functions)
and to its daily-life impacts (retentissements) — see spec 4.5.2.
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.cognition import (
    FonctionCognitive,
    RetentissementVieQuotidienne,
    SousFonction,
    trouble_retentissements,
    trouble_sous_fonctions,
)


class Trouble(Base):
    __tablename__ = "troubles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # L'ADAPT mapping (nullable: unmapped troubles allowed during migration).
    fonction_id: Mapped[int | None] = mapped_column(
        ForeignKey("fonctions_cognitives.id", ondelete="SET NULL"), default=None
    )
    fonction: Mapped[FonctionCognitive | None] = relationship(lazy="selectin")
    sous_fonctions: Mapped[list[SousFonction]] = relationship(
        secondary=trouble_sous_fonctions, lazy="selectin"
    )
    retentissements: Mapped[list[RetentissementVieQuotidienne]] = relationship(
        secondary=trouble_retentissements, lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Trouble {self.name}>"


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Theme {self.name}>"
