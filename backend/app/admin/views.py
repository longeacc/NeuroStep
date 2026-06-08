"""SQLAdmin backoffice (Phase 0 admin panel; React backoffice comes in Phase 1).

Mounted at /admin. Login uses an app User with ADMIN role.
"""

from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.requests import Request

from app.core.security import (
    TOKEN_ACCESS,
    create_access_token,
    decode_token,
    verify_password,
)
from app.db.session import SessionLocal, engine
from app.models.application import Application
from app.models.cognition import (
    FonctionCognitive,
    RetentissementVieQuotidienne,
    SousFonction,
)
from app.models.evaluation import Evaluation
from app.models.prescription import Prescription, PrescriptionItem
from app.models.relation import RelationTherapeutique
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
        email = decode_token(token, TOKEN_ACCESS)
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
    column_list = [Trouble.id, Trouble.name, Trouble.fonction]


class FonctionCognitiveAdmin(ModelView, model=FonctionCognitive):
    name = "Fonction cognitive"
    name_plural = "Fonctions cognitives"
    column_list = [
        FonctionCognitive.id,
        FonctionCognitive.nom,
        FonctionCognitive.is_motrice,
    ]


class SousFonctionAdmin(ModelView, model=SousFonction):
    name = "Sous-fonction"
    name_plural = "Sous-fonctions"
    column_list = [SousFonction.id, SousFonction.nom, SousFonction.fonction]


class RetentissementAdmin(ModelView, model=RetentissementVieQuotidienne):
    name = "Retentissement"
    name_plural = "Retentissements"
    column_list = [
        RetentissementVieQuotidienne.id,
        RetentissementVieQuotidienne.libelle,
    ]


class ThemeAdmin(ModelView, model=Theme):
    column_list = [Theme.id, Theme.name]


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.role, User.is_active, User.is_verified]
    column_searchable_list = [User.email]


class RelationAdmin(ModelView, model=RelationTherapeutique):
    name = "Relation thérapeutique"
    name_plural = "Relations thérapeutiques"
    column_list = [
        RelationTherapeutique.id,
        RelationTherapeutique.ergo_id,
        RelationTherapeutique.patient_id,
        RelationTherapeutique.active,
    ]


class EvaluationAdmin(ModelView, model=Evaluation):
    column_list = [
        Evaluation.id,
        Evaluation.application_id,
        Evaluation.user_id,
        Evaluation.pertinence_clinique,
        Evaluation.efficacite,
    ]


class PrescriptionAdmin(ModelView, model=Prescription):
    column_list = [
        Prescription.id,
        Prescription.ergo_id,
        Prescription.patient_id,
        Prescription.status,
    ]


class PrescriptionItemAdmin(ModelView, model=PrescriptionItem):
    name = "Item de prescription"
    name_plural = "Items de prescription"
    column_list = [
        PrescriptionItem.id,
        PrescriptionItem.prescription_id,
        PrescriptionItem.application_id,
        PrescriptionItem.priorite,
    ]


def setup_admin(app, secret_key: str) -> Admin:
    admin = Admin(
        app,
        engine,
        authentication_backend=AdminAuth(secret_key=secret_key),
        title="Neurostep Admin",
    )
    admin.add_view(ApplicationAdmin)
    admin.add_view(TroubleAdmin)
    admin.add_view(FonctionCognitiveAdmin)
    admin.add_view(SousFonctionAdmin)
    admin.add_view(RetentissementAdmin)
    admin.add_view(ThemeAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(RelationAdmin)
    admin.add_view(EvaluationAdmin)
    admin.add_view(PrescriptionAdmin)
    admin.add_view(PrescriptionItemAdmin)
    return admin
