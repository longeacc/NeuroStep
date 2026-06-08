"""Schemas de prescription numérique (spec 5.4)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalogue import ApplicationRead


class PrescriptionItemCreate(BaseModel):
    application_id: int
    consignes: str | None = None
    priorite: int = Field(default=2, ge=1, le=3)  # 1 = haute, 3 = basse


class PrescriptionCreate(BaseModel):
    patient_id: int
    notes: str | None = None
    items: list[PrescriptionItemCreate] = Field(min_length=1)


class PrescriptionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    consignes: str | None
    priorite: int
    feedback_patient: str | None
    application: ApplicationRead


class PrescriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ergo_id: int
    patient_id: int
    status: str
    notes: str | None
    share_token: str | None
    created_at: datetime
    validated_at: datetime | None
    items: list[PrescriptionItemRead]


class FeedbackCreate(BaseModel):
    feedback: str = Field(min_length=1)
