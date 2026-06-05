# Neurostep

**Catalogue numérique d'API / Outils pour Cérébrolésés & Tumeurs**

Outil développé dans le cadre du Hackathon SN@SU. Il permet d'accumuler, classifier et rechercher des applications de compensation cognitive (Aide à la communication, Mémoire, Planification, etc.).

## Lancer le projet

```bash
# 1. Créer un environnement virtuel (optionnel mais recommandé)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
streamlit run app.py
```

## Architecture

Toutes les données sont stockées au format `.json` pour faciliter la gestion et l'évolution de la base sans SQL. 

- `app.py` : L'interface utilisateur et administrateur (Streamlit)
- `database.py` : Le gestionnaire de la base de données JSON
- `data/database.json` : Les applications, troubles et thèmes répertoriés

