# 🧠 Neurostep

**Plateforme de compensation des fonctions cognitives**

Hackathon SN@SU — 5 juin 2026 · Clément Longeac · ESIEE Paris / DuraXELL

---

## Le problème

2 millions de Français vivent avec des séquelles cognitives (AVC, TCC, tumeurs cérébrales). Les ergothérapeutes disposent de centaines d'applications de compensation cognitive, mais aucun point d'entrée unique pour les identifier, comparer et prescrire.

## La solution

Neurostep est une plateforme de recherche sémantique locale qui permet de trouver les outils adaptés au profil cognitif d'un patient en langage naturel.

## Démarrage rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Initialiser la base et les données de démo
python generate_seed_data.py

# 3. (Optionnel) Télécharger le modèle sémantique (meilleure pertinence)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# 4. Lancer l'application
streamlit run app.py
```

> Si le modèle sémantique n'est pas disponible, un fallback TF-IDF est activé automatiquement.

## Architecture

```
neurostep/
├── app.py                    # Application Streamlit (4 pages)
├── database.py               # Gestionnaire SQLite (CRUD complet)
├── search_engine.py          # Moteur de recherche (sémantique + fallback TF-IDF)
├── generate_seed_data.py     # 20 applications de démonstration
├── schema.sql                # Schéma SQLite
├── requirements.txt          # Dépendances Python
├── .gitignore
├── neurostep.db              # (généré) Base de données locale
└── embeddings.pkl            # (généré) Cache des vecteurs d'index
```

## RGPD

Toutes les données restent sur la machine locale. Aucun backend externe, aucune API cloud, aucun LLM distant. Les patients sont identifiés par UUID local uniquement.

## Stack

Python 3.10+ · Streamlit · SQLite · scikit-learn · sentence-transformers (optionnel)

## Licence

MIT
