"""Pytest fixtures: isolated SQLite test DB, seeded once, + auth helpers."""

import os

# Configure the app for testing BEFORE any app module is imported.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_neurostep.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

API = "/api/v1"


@pytest.fixture(scope="session", autouse=True)
def _seeded_db():
    """Fresh schema + full seed (admin, legacy catalogue, L'ADAPT) for the session."""
    import app.models  # noqa: F401  (register metadata)
    from app import seed
    from app.db.base import Base
    from app.db.session import SessionLocal, engine

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed.seed_admin(db)
        seed.seed_from_legacy(db)
        seed.seed_ladapt(db)
        db.commit()
    yield
    Base.metadata.drop_all(engine)
    engine.dispose()
    try:
        os.remove("./test_neurostep.db")
    except OSError:
        pass


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


# --- auth helpers ---
def verify_token_for(email: str) -> str:
    from app.core.security import create_email_verify_token

    return create_email_verify_token(email)


def register_verified(client: TestClient, email: str, role: str = "ergo", pw: str = "secret1") -> None:
    client.post(f"{API}/users/register", json={"email": email, "password": pw, "role": role})
    client.post(f"{API}/auth/verify-email?token={verify_token_for(email)}")


def login(client: TestClient, email: str, pw: str = "secret1") -> str:
    r = client.post(f"{API}/auth/login", data={"username": email, "password": pw})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_token(client):
    from app.core.config import settings

    return login(client, settings.FIRST_ADMIN_EMAIL, settings.FIRST_ADMIN_PASSWORD)


@pytest.fixture
def ergo_token(client):
    register_verified(client, "ergo_fixture@x.fr", role="ergo")
    return login(client, "ergo_fixture@x.fr")
