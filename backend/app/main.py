"""Neurostep API — FastAPI application factory.

Phase 0 skeleton reproducing the Streamlit prototype (catalogue + admin)
on a production-ready, modular architecture.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.views import setup_admin
from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

# Ensure all models are registered on Base.metadata.
import app.models  # noqa: F401,E402


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Skeleton: create tables on startup. Production uses Alembic migrations.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Catalogue d'outils numeriques pour cerebroleses / tumeur.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# SQLAdmin backoffice at /admin
setup_admin(app, secret_key=settings.SECRET_KEY)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "env": settings.ENVIRONMENT}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
