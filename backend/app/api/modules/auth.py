"""Auth module: login, refresh, logout, email verification.

JWT scheme: short-lived access token (15 min) returned in the body; long-lived
refresh token (7 days) stored in a secure httpOnly cookie.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core.config import settings
from app.core.security import (
    TOKEN_EMAIL_VERIFY,
    TOKEN_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token

router = APIRouter()


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path=f"{settings.API_V1_PREFIX}/auth",
    )


@router.post("/login", response_model=Token)
def login(
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """OAuth2 password grant. `username` field = email."""
    user = db.scalar(select(User).where(User.email == form.username))
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    _set_refresh_cookie(response, create_refresh_token(subject=user.email))
    return Token(access_token=create_access_token(subject=user.email))


@router.post("/refresh", response_model=Token)
def refresh(
    request: Request, response: Response, db: Session = Depends(get_db)
) -> Token:
    """Exchange the refresh cookie for a fresh access token (and rotate refresh)."""
    cookie = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not cookie:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    email = decode_token(cookie, TOKEN_REFRESH)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    _set_refresh_cookie(response, create_refresh_token(subject=user.email))  # rotation
    return Token(access_token=create_access_token(subject=user.email))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(
        settings.REFRESH_COOKIE_NAME, path=f"{settings.API_V1_PREFIX}/auth"
    )


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(token: str, db: Session = Depends(get_db)) -> dict:
    """Confirm an email-verification token (Phase 0)."""
    email = decode_token(token, TOKEN_EMAIL_VERIFY)
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.commit()
    return {"status": "verified", "email": email}
