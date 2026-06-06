"""Application/tool catalogue model (core of the Streamlit prototype)."""

from sqlalchemy import Boolean, Column, ForeignKey, JSON, String, Table, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.taxonomy import Theme, Trouble

# jsonb on PostgreSQL (indexable, native operators); plain JSON on SQLite (dev).
JSONType = JSON().with_variant(JSONB, "postgresql")

# Many-to-many: an application targets several troubles.
application_troubles = Table(
    "application_troubles",
    Base.metadata,
    Column("application_id", ForeignKey("applications.id", ondelete="CASCADE"), primary_key=True),
    Column("trouble_id", ForeignKey("troubles.id", ondelete="CASCADE"), primary_key=True),
)

# Many-to-many: an application belongs to several activity themes.
application_themes = Table(
    "application_themes",
    Base.metadata,
    Column("application_id", ForeignKey("applications.id", ondelete="CASCADE"), primary_key=True),
    Column("theme_id", ForeignKey("themes.id", ondelete="CASCADE"), primary_key=True),
)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(512), index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None)
    objectif_ther: Mapped[str | None] = mapped_column(Text, default=None)
    image: Mapped[str | None] = mapped_column(String(1024), default=None)
    url_store: Mapped[str | None] = mapped_column(String(1024), default=None)
    gratuit: Mapped[bool] = mapped_column(Boolean, default=False)
    enrichi: Mapped[bool] = mapped_column(Boolean, default=False)
    # Supported OS/platforms kept as a jsonb array (small closed enum set).
    plateformes: Mapped[list[str]] = mapped_column(JSONType, default=list)

    troubles: Mapped[list[Trouble]] = relationship(
        secondary=application_troubles, lazy="selectin"
    )
    themes: Mapped[list[Theme]] = relationship(
        secondary=application_themes, lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Application {self.id} {self.nom!r}>"
