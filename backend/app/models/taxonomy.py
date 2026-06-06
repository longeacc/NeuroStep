"""Reference taxonomies: Trouble (pathology) and Theme (activity area)."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Trouble(Base):
    __tablename__ = "troubles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Trouble {self.name}>"


class Theme(Base):
    __tablename__ = "themes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Theme {self.name}>"
