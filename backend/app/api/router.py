"""Aggregate API v1 router."""

from fastapi import APIRouter

from app.api.modules import auth, catalogue, evaluation, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(catalogue.router, prefix="/applications", tags=["catalogue"])
api_router.include_router(evaluation.router, prefix="/evaluations", tags=["evaluation"])
