"""Shared API dependencies: auth, RBAC role guards, cloisonnement."""

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import TOKEN_ACCESS, decode_token
from app.db.session import get_db
from app.models.relation import RelationTherapeutique
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")

_credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    email = decode_token(token, TOKEN_ACCESS)
    if email is None:
        raise _credentials_exc
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active:
        raise _credentials_exc
    return user


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    """Dependency factory enforcing the caller holds one of `roles`."""

    def _guard(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role in {[r.value for r in roles]}",
            )
        return user

    return _guard


# Convenience guards.
require_admin = require_roles(UserRole.ADMIN)
require_ergo = require_roles(UserRole.ERGO)
require_patient = require_roles(UserRole.PATIENT)


def ensure_active_relation(ergo: User, patient_id: int, db: Session) -> None:
    """Cloisonnement (medical secret): raise 403 unless `ergo` has an active
    therapeutic relation with `patient_id`. Admins bypass (aggregated access)."""
    if ergo.role == UserRole.ADMIN:
        return
    rel = db.scalar(
        select(RelationTherapeutique).where(
            and_(
                RelationTherapeutique.ergo_id == ergo.id,
                RelationTherapeutique.patient_id == patient_id,
                RelationTherapeutique.active.is_(True),
            )
        )
    )
    if rel is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active therapeutic relation with this patient",
        )
