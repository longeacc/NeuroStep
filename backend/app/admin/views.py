"""SQLAdmin backoffice (Phase 0 admin panel; React backoffice comes in Phase 1).

Mounted at /admin. Login uses an app User with ADMIN role.
"""

from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.requests import Request

from app.core.security import create_access_token, decode_access_token, verify_password
from app.db.session import SessionLocal, engine
from app.models.application import Application
from app.models.evaluation import Evaluation
from app.models.taxonomy import Theme, Trouble
from app.models.user import User, UserRole


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form.get("username"), form.get("password")
        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.email == email))
            if (
                user
                and user.role == UserRole.ADMIN
                and verify_password(str(password), user.hashed_password)
            ):
                request.session["token"] = create_access_token(subject=user.email)
                return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        email = decode_access_token(token)
        if not email:
            return False
        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.email == email))
            return bool(user and user.role == UserRole.ADMIN)


class ApplicationAdmin(ModelView, model=Application):
    name = "Application"
    name_plural = "Applications"
    column_list = [Application.id, Application.nom, Application.gratuit, Application.enrichi]
    column_searchable_list = [Application.nom]
    column_sortable_list = [Application.id, Application.nom]


class TroubleAdmin(ModelView, model=Trouble):
    column_list = [Trouble.id, Trouble.name]


class ThemeAdmin(ModelView, model=Theme):
    column_list = [Theme.id, Theme.name]


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.role, User.is_active]
    column_searchable_list = [User.email]


class EvaluationAdmin(ModelView, model=Evaluation):
    column_list = [Evaluation.id, Evaluation.application_id, Evaluation.user_id, Evaluation.rating]


def setup_admin(app, secret_key: str) -> Admin:
    admin = Admin(
        app,
        engine,
        authentication_backend=AdminAuth(secret_key=secret_key),
        title="Neurostep Admin",
    )
    admin.add_view(ApplicationAdmin)
    admin.add_view(TroubleAdmin)
    admin.add_view(ThemeAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(EvaluationAdmin)
    return admin
