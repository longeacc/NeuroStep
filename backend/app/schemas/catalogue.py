"""Catalogue schemas: Application, Trouble, Theme (Pydantic v2)."""

from pydantic import BaseModel, ConfigDict


class SousFonctionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nom: str


class FonctionCognitiveRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nom: str
    is_motrice: bool
    sous_fonctions: list[SousFonctionRead] = []


class RetentissementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    libelle: str


class TroubleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    fonction: FonctionCognitiveRead | None = None
    sous_fonctions: list[SousFonctionRead] = []
    retentissements: list[RetentissementRead] = []


class ThemeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ApplicationBase(BaseModel):
    nom: str
    description: str | None = None
    objectif_ther: str | None = None
    image: str | None = None
    url_store: str | None = None
    gratuit: bool = False
    enrichi: bool = False
    plateformes: list[str] = []


class ApplicationCreate(ApplicationBase):
    # Troubles referenced by name (matches the prototype's free-text taxonomy).
    troubles: list[str] = []


class ApplicationUpdate(BaseModel):
    nom: str | None = None
    description: str | None = None
    objectif_ther: str | None = None
    image: str | None = None
    url_store: str | None = None
    gratuit: bool | None = None
    enrichi: bool | None = None
    plateformes: list[str] | None = None
    troubles: list[str] | None = None


class ApplicationRead(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    troubles: list[TroubleRead] = []
    themes: list[ThemeRead] = []
