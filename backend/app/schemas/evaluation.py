"""Evaluation schemas (Phase 1 placeholder)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvaluationCreate(BaseModel):
    application_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class EvaluationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    user_id: int
    rating: int
    comment: str | None
    created_at: datetime
