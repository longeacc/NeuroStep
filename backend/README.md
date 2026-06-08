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
| DB           | PostgreSQL 16 (prod) / SQLite (dev) |
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
  api/         deps (RBAC guards, cloisonnement), router, modules/{auth,users,catalogue,evaluation,relations}
  admin/       SQLAdmin views + auth backend
  main.py      app factory
  seed.py      data migration: ../data/database.json -> relational DB
alembic/       migrations (schema + PG extensions)
```

## Correspondance avec l'arborescence de la spec (§4.6)

La structure est plus modulaire que le plan illustratif de la spec ; chaque élément a
son équivalent :

| Spec                                   | Implémentation réelle                         |
|----------------------------------------|-----------------------------------------------|
| `app/config.py`                        | `app/core/config.py`                          |
| `app/database.py`                      | `app/db/session.py` + `app/db/base.py`        |
| `models/trouble.py`                    | `app/models/taxonomy.py` (Trouble + Theme)    |
| `models/fonction_cognitive.py`         | `app/models/cognition.py`                     |
| `models/{prescription,suivi}.py`       | Phase 1 (non encore créés)                    |
| `schemas/application.py`               | `app/schemas/catalogue.py`                     |
| `routers/`                             | `app/api/modules/` (auth, catalogue, users, evaluation, relations) |
| `routers/admin.py`                     | `app/admin/` (SQLAdmin) + guards `require_admin` |
| `services/search.py`                   | `app/services/catalogue.py`                    |
| `services/{prescription,export_pdf}.py`| Phase 1                                        |
| `middleware/{auth,rbac}.py`            | `app/api/deps.py` (dépendances FastAPI — RBAC par route, plus idiomatique) |
| `app/migrations/`                      | `backend/alembic/` (convention Alembic)        |
| `tests/`                               | `backend/tests/` (pytest, voir ci-dessous)     |
| `frontend/`                            | Phase 0 (S8+), non démarré                      |

Choix de conception : le contrôle d'accès passe par des **dépendances** FastAPI
(`require_roles`, `ensure_active_relation`) plutôt qu'un middleware global — le contrôle
est attaché par route, visible dans Swagger et testable unitairement.

## Tests & couverture

```bash
cd backend
pip install -r requirements-dev.txt
pytest                      # avec couverture (seuil 80% — voir pytest.ini)
```

## Auth & RBAC (spec 4.4)

- **Roles**: `admin` (catalogue/taxonomy/accounts/stats), `ergo` (ergothérapeute —
  prescriptions, patient follow-up), `patient` (recommended tools, feedback).
  Guards: `require_roles(...)` in `app/api/deps.py`.
- **JWT**: 15-min access token (response body) + 7-day refresh token in a secure
  **httpOnly cookie**; `/auth/refresh` rotates it, `/auth/logout` clears it.
- **Email verification** (Phase 0): registration creates an unverified account; login
  is blocked until `/auth/verify-email`. Email delivery is stubbed (`services/email.py`,
  logs the link) — swap for SMTP / Scaleway TEM in prod.
- **Cloisonnement (secret médical)**: an ergo only accesses data of patients with an
  *active* `relations_therapeutiques` row — enforced by `ensure_active_relation()`.
  Admins see aggregated data only.
- Phase 2: Pro Santé Connect (ANS SSO) replaces email/password for professionals.

## Quickstart (local, zero infra — SQLite)

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate      # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env                              # defaults to sqlite
python -m app.seed                                  # creates schema + admin + imports legacy JSON
uvicorn app.main:app --reload
```

- Swagger / OpenAPI : http://127.0.0.1:8000/docs
- Admin backoffice  : http://127.0.0.1:8000/admin  (admin@neurostep.app / admin)
- Health            : http://127.0.0.1:8000/health

## Full stack (PostgreSQL + Redis + MinIO)

```bash
cd backend
docker compose up --build -d
docker compose exec api alembic upgrade head      # schema + PG extensions
docker compose exec api python -m app.seed        # data only on PostgreSQL
```

On PostgreSQL the schema and `unaccent`/`pg_trgm`/`pgvector` extensions are owned by
**Alembic** (`alembic upgrade head`); the app no longer auto-creates tables. On SQLite
the seed auto-creates the schema for zero-friction dev.

**Hosting** (spec 4.3.3): Phase 0–1 on Scaleway (Paris) with managed PostgreSQL — valid
while no identifying patient data is processed. Phase 2+ requires migration to a
certified **HDS** host (OVHcloud Healthcare / Outscale 3DS / Azure France) before any
personal health data (art. L.1111-8 CSP).

## API (v1, prefix `/api/v1`)

| Method | Path                                   | Auth   | Description                       |
|--------|----------------------------------------|--------|-----------------------------------|
| POST   | `/auth/login`                          | —      | OAuth2 password → access token + refresh cookie |
| POST   | `/auth/refresh`                        | cookie | Rotate refresh → new access token |
| POST   | `/auth/logout`                         | —      | Clear refresh cookie              |
| POST   | `/auth/verify-email?token=`            | —      | Confirm email verification        |
| POST   | `/users/register`                      | —      | Register (ergo / patient)         |
| GET    | `/users/me`                            | JWT    | Current profile                   |
| GET    | `/applications`                        | —      | List + filters `q`, `os`, `trouble` |
| GET    | `/applications/{id}`                   | —      | Detail                            |
| POST   | `/applications`                        | admin  | Create tool                       |
| PUT    | `/applications/{id}`                   | admin  | Update tool                       |
| GET    | `/applications/_meta/troubles`         | —      | Pathology taxonomy                |
| GET    | `/applications/_meta/themes`           | —      | Activity-area taxonomy            |
| GET    | `/applications/_meta/fonctions`        | —      | L'ADAPT cognitive functions + sub-functions |
| GET    | `/applications/_meta/retentissements`  | —      | Retentissements en vie quotidienne |
| GET    | `/applications/search`                 | —      | Recherche multi-critères enrichie (spec 5.3) |
| POST   | `/relations`                           | ergo   | Open therapeutic relation w/ patient |
| GET    | `/relations`                           | ergo   | My patients                       |
| DELETE | `/relations/{patient_id}`              | ergo   | End relation (revoke access)      |
| POST   | `/evaluations`                         | ergo   | Évaluation multi-axes (5 axes + commentaires) |
| GET    | `/evaluations/application/{id}`        | —      | Évaluations d'un outil            |
| GET    | `/evaluations/application/{id}/summary`| —      | Moyennes agrégées par axe         |
| POST   | `/prescriptions`                       | ergo   | Créer une prescription (relation requise) |
| GET    | `/prescriptions`                       | ergo   | Mes prescriptions                 |
| GET    | `/prescriptions/{id}`                  | ergo/patient | Détail                      |
| POST   | `/prescriptions/{id}/validate`         | ergo   | Valider → jeton de partage        |
| GET    | `/prescriptions/{id}/pdf`              | ergo/patient | Export PDF (reportlab + QR)  |
| GET    | `/prescriptions/shared/{token}`        | —      | Accès patient (lien sécurisé)     |
| POST   | `/prescriptions/shared/{token}/items/{item_id}/feedback` | — | Feedback d'usage patient |

## Data migration — L'ADAPT taxonomy (spec 4.5)

`python -m app.seed` runs the full migration, idempotently:

1. Extract legacy `data/database.json`.
2. Build the L'ADAPT cognitive taxonomy: **functions → sub-functions**
   (`app/data/ladapt.py`).
3. Map each legacy trouble onto a function + sub-functions (table 4.5.2), e.g.
   *Aphasie → Langage oral / {Production, Réception}*. `Hémiplégie` is motor, kept under
   a flagged **Compensation motrice** function (`is_motrice=True`).
4. `retentissements` (daily-life impacts) table is created; seeding awaits the L'ADAPT
   PDF source.
5. Insert applications with **M:N** links to troubles and themes.
6. Referential-integrity check printed at the end (counts + any unmapped trouble).

Models: `FonctionCognitive`, `SousFonction`, `RetentissementVieQuotidienne`,
`Trouble.fonction` / `.sous_fonctions` / `.retentissements`, `Application.themes`.

> **Note** — table 4.5.2 yields **5** cognitive domains; the validation target is 7.
> The remaining 2 live only in the L'ADAPT PDF — add them to `LADAPT_FONCTIONS` /
> `TROUBLE_MAPPING` once sourced (no code change needed).

## Search (`GET /applications?q=...`)

Dialect-aware, behind the same endpoint:

- **PostgreSQL 16** — French full-text (`to_tsvector('french', …)` + `websearch_to_tsquery`)
  combined with `unaccent` (accent-insensitive) and `pg_trgm` `similarity()` for typo
  tolerance. Extensions + a GIN trigram index on `applications.nom` are created by the
  Alembic migration. `plateformes` stored as `jsonb`.
- **SQLite (dev)** — portable `ILIKE` fallback, no extensions required.

`pgvector` is enabled best-effort (image `pgvector/pgvector:pg16`) and reserved for
Phase 2 semantic search.

## Recherche multi-critères enrichie — `GET /applications/search` (spec 5.3)

Recherche croisée combinable (tous les critères sont optionnels et cumulables) :

| Paramètre        | Effet |
|------------------|-------|
| `q`              | full-text FR (nom + description + objectif) — PG ; `ILIKE` en dev SQLite |
| `fonction`       | fonction cognitive L'ADAPT (ex. `Attention`) |
| `sous_fonction`  | sous-fonction (ex. `Réception`) |
| `trouble`        | pathologie (ex. `Aphasie`) |
| `retentissement` | retentissement en vie quotidienne (ex. « Ne peut pas suivre une procédure écrite ») |
| `plateformes`    | répétable : `?plateformes=Web&plateformes=iOS` (intersection) |
| `gratuit`        | `true` / `false` |
| `objectif`       | texte dans l'objectif thérapeutique |

Sur PostgreSQL : `to_tsvector('french', f_unaccent(...))` + `plainto_tsquery`, tri par
`ts_rank`. L'index GIN `idx_app_search` (migration `0002`) couvre **exactement** la même
expression (`f_unaccent` = wrapper IMMUTABLE autour de `unaccent`, requis pour un index
d'expression). Index GIN `idx_app_plateformes` sur le jsonb des plateformes.

## CI/CD

`.github/workflows/ci.yml` (sur push / PR vers `main`) : **lint ruff → pytest (couverture
≥80%) → build de l'image Docker backend**. Étape staging Scaleway à brancher en S10.

## Prescription numérique (spec 5.4)

Workflow ergothérapeute → patient, cloisonné par la relation thérapeutique :

1. L'ergo crée une prescription (statut `draft`) : patient + 1..N outils, chacun avec
   **consignes** personnalisées et **priorité** (1 haute → 3 basse). La création exige
   une `relation_therapeutique` active (sinon 403).
2. `POST /prescriptions/{id}/validate` → statut `validated` + **jeton de partage** (`secrets`).
3. **PDF serveur** (`GET /{id}/pdf`) via **reportlab + qrcode** : identité prescripteur
   (nom, établissement, RPPS), date, outils + consignes, fiches résumées (avantages/limites),
   et un **QR code** vers la version interactive (`FRONTEND_URL/p/{token}`).
4. **Lien sécurisé patient** (`/shared/{token}`, sans auth) : consultation + **feedback
   d'usage** par outil.

> weasyprint a été écarté (dépendances système GTK/Pango/Cairo) au profit de reportlab,
> pur Python et portable Windows/Docker.

## Évaluations multi-axes (spec 5.5)

`POST /evaluations` (réservé `ergo`) : **5 axes** notés 1–5 (pertinence clinique,
utilisabilité, efficacité, accessibilité, intégration) + **commentaires structurés**
(avantages, limites, contexte d'utilisation, profil patient type). Chaque évaluation
expose sa `moyenne` et `auteur_rpps_verifie` (crédibilité : pro à **RPPS vérifié**).
`GET /evaluations/application/{id}/summary` renvoie les moyennes agrégées par axe.

## Next steps (Phase 1)
- React backoffice replacing SQLAdmin.
- Prescription + Suivi Patient modules.
- Semantic search (sentence-transformers) over the catalogue.
- S3/MinIO upload pipeline for tool images (currently stored as URLs).


## Command :

cd backend
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.seed
uvicorn app.main:app --reload


1 register ergo 201   2 login-unverified 403   3 verify-email 200
4 login 200 +refresh cookie   5 me role=ergo   6 refresh 200 (new access)
7 patient id 4   8 create relation 201   9 ergo→create app 403 (RBAC)
10 admin→create app 201   11 logout 204
