"""User model — platform users under RBAC (admin / ergothérapeute / patient)."""

import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"        # platform administrator (catalogue, taxonomy, accounts, stats)
    ERGO = "ergo"          # ergothérapeute (prescriptions, patient follow-up)
    PATIENT = "patient"    # patient (recommended tools, simplified sheets, feedback)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255), default=None)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.ERGO, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Phase 0: email/password auth with email verification.
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email} ({self.role.value})>"
