"""Therapeutic-relation schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RelationCreate(BaseModel):
    patient_id: int


class RelationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ergo_id: int
    patient_id: int
    active: bool
    created_at: datetime
