# NeuroStep — Frontend (Phase 1)

Frontend Next.js 14 (App Router) du catalogue NeuroStep — squelette + page Catalogue
connectée au backend FastAPI + connexion JWT.

## Stack (spec 5.2)

| Élément        | Choix                                  |
|----------------|----------------------------------------|
| Framework      | Next.js 14 (App Router, TypeScript)    |
| Styles         | Tailwind CSS                           |
| Composants UI  | Shadcn/UI (Radix + CVA)                |
| Cache API      | TanStack Query                         |
| State          | Zustand (`auth`, `filters`)            |
| Mobile patient | PWA installable (`manifest.webmanifest`) |

## Démarrage

```bash
cd frontend
npm install
cp .env.example .env.local         # NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
npm run dev                        # http://localhost:3000
```

> Nécessite le backend lancé sur `:8000` (voir `backend/README.md`). Le CORS backend
> autorise `http://localhost:3000` avec credentials (cookie refresh).

## Arborescence

```
src/
  app/
    layout.tsx          # layout + Providers + Navbar
    providers.tsx       # QueryClient + restauration de session (refresh)
    page.tsx            # accueil = catalogue
    login/page.tsx      # connexion JWT
  components/
    ui/                 # Shadcn (button, card, input, badge, label, select)
    catalogue/          # catalogue-view, application-card
    navbar.tsx
  lib/
    api.ts              # client fetch (Authorization Bearer + credentials)
    auth.ts             # login / refresh / logout / me
    queries.ts          # hooks TanStack Query (catalogue, troubles)
    types.ts            # types miroir des schémas backend
  stores/
    auth.ts             # token d'accès (mémoire) + user
    filters.ts          # filtres catalogue
```

## Fonctionnalités livrées

- **Catalogue** : liste des applications, filtres **support (OS)** et **trouble**,
  **recherche** texte — branchés sur `GET /api/v1/applications` (mêmes filtres que l'API).
- **Connexion** : OAuth2 password → access token (mémoire) + refresh cookie httpOnly ;
  session restaurée au rechargement via `/auth/refresh`.
- **PWA** : manifest installable (le service worker offline est un *next step*).

## Sécurité

L'access token (court, 15 min) reste **en mémoire** (Zustand), pas en `localStorage`
(réduit la surface XSS). Le refresh token est un cookie **httpOnly** géré par le backend.
En prod multi-domaine (`app.` ↔ `api.neurostep.fr`), passer le cookie en
`SameSite=None; Secure` (config backend `COOKIE_SAMESITE` / `COOKIE_SECURE`).

## Next steps (Phase 1)

- Back-office admin (CRUD applications, taxonomie) — réservé au rôle `admin`.
- Module prescription + parcours patient (PWA hors-ligne, service worker).
- Détail d'un outil (fonctions cognitives L'ADAPT, retentissements).
- Tests composants (Vitest / Testing Library) + intégration au workflow CI.
