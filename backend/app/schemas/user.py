"""User schemas (Pydantic v2)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str | None = None
    role: UserRole = UserRole.ERGO  # self-registration: ergo (default) or patient


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None
    role: UserRole
    is_active: bool
    is_verified: bool
    etablissement: str | None = None
    rpps: str | None = None
    rpps_verified: bool = False
    created_at: datetime
