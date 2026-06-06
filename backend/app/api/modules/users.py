"""Users module: registration (+ email verification) and current profile."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_email_verify_token, hash_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserRead
from app.services.email import send_verification_email

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="Email already registered")
    # Self-registration limited to ergo/patient; admins are provisioned, not self-signed.
    if payload.role not in (UserRole.ERGO, UserRole.PATIENT):
        raise HTTPException(status_code=422, detail="Invalid self-registration role")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    send_verification_email(user.email, create_email_verify_token(user.email))
    return user


@router.get("/me", response_model=UserRead)
def me(current: User = Depends(get_current_user)) -> User:
    return current
