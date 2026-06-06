"""Password hashing + JWT helpers (access / refresh / email-verification tokens)."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token "type" claim — guards against using one token kind where another is expected.
TOKEN_ACCESS = "access"
TOKEN_REFRESH = "refresh"
TOKEN_EMAIL_VERIFY = "email_verify"


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _encode(subject: str, token_type: str, expires: timedelta) -> str:
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": datetime.now(timezone.utc) + expires,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str) -> str:
    return _encode(
        subject, TOKEN_ACCESS, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(subject: str) -> str:
    return _encode(
        subject, TOKEN_REFRESH, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def create_email_verify_token(subject: str) -> str:
    return _encode(
        subject, TOKEN_EMAIL_VERIFY, timedelta(hours=settings.EMAIL_VERIFY_EXPIRE_HOURS)
    )


def decode_token(token: str, expected_type: str) -> str | None:
    """Return subject if valid and of the expected type, else None."""
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    return payload.get("sub")
