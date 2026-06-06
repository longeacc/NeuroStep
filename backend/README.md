# Neurostep — Backend API (Phase 0)

FastAPI backend reproducing the Streamlit prototype (catalogue d'outils numériques
pour cérébrolésés / tumeur) on a production-ready, modular architecture.

## Architecture

```
CLIENT (Next.js)  ──HTTPS/JWT──►  API GATEWAY (FastAPI)
                                  ├─ Auth        module
                                  ├─ Users       module
                                  ├─ Catalogue   module
                                  ├─ Évaluation  module (Phase 1 skeleton)
                                  └─ /admin      (SQLAdmin backoffice)
                                        │
                          ┌─────────────┼──────────────┐
                     PostgreSQL       Redis        S3 / MinIO
                     (données)     (cache/sess.)   (images/fichiers)
```

| Layer        | Choice                              |
|--------------|-------------------------------------|
| Framework    | FastAPI 0.110+ (ASGI / uvicorn)     |
| Validation   | Pydantic v2                         |
| ORM          | SQLAlchemy 2.0                      |
| DB           | PostgreSQL (prod) / SQLite (dev)    |
| Auth         | OAuth2 password flow + JWT          |
| Admin panel  | SQLAdmin (Phase 0)                  |
| Migrations   | Alembic-ready (create_all in skel.) |

## Project layout

```
backend/app/
  core/        config (pydantic-settings) + security (JWT, bcrypt)
  db/          engine, session, declarative base
  models/      User, Application, Trouble, Theme, Evaluation
  schemas/     Pydantic v2 request/response models
  services/    catalogue query + taxonomy resolution
  api/         deps (auth guards), router, modules/{auth,users,catalogue,evaluation}
  admin/       SQLAdmin views + auth backend
  main.py      app factory
  seed.py      data migration: ../data/database.json -> relational DB
```

## Quickstart (local, zero infra — SQLite)

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate      # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env                              # defaults to sqlite
python -m app.seed                                  # migrate legacy JSON + create admin
uvicorn app.main:app --reload
```

- Swagger / OpenAPI : http://127.0.0.1:8000/docs
- Admin backoffice  : http://127.0.0.1:8000/admin  (admin@neurostep.app / admin)
- Health            : http://127.0.0.1:8000/health

## Full stack (PostgreSQL + Redis + MinIO)

```bash
cd backend
docker compose up --build -d
docker compose exec api python -m app.seed
```

## API (v1, prefix `/api/v1`)

| Method | Path                                   | Auth   | Description                       |
|--------|----------------------------------------|--------|-----------------------------------|
| POST   | `/auth/login`                          | —      | OAuth2 password → JWT             |
| POST   | `/users/register`                      | —      | Register a professional           |
| GET    | `/users/me`                            | JWT    | Current profile                   |
| GET    | `/applications`                        | —      | List + filters `q`, `os`, `trouble` |
| GET    | `/applications/{id}`                   | —      | Detail                            |
| POST   | `/applications`                        | admin  | Create tool                       |
| PUT    | `/applications/{id}`                   | admin  | Update tool                       |
| GET    | `/applications/_meta/troubles`         | —      | Pathology taxonomy                |
| GET    | `/applications/_meta/themes`           | —      | Activity-area taxonomy            |
| POST   | `/evaluations`                         | JWT    | Rate a tool (Phase 1)             |
| GET    | `/evaluations/application/{id}`        | —      | Evaluations for a tool            |

## Next steps (Phase 1)
- Replace `create_all` with Alembic migration history.
- React backoffice replacing SQLAdmin.
- Prescription + Suivi Patient modules.
- Semantic search (sentence-transformers) over the catalogue.
- S3/MinIO upload pipeline for tool images (currently stored as URLs).
