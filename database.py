"""
database.py — Gestionnaire SQLite pour Neurostep
─────────────────────────────────────────────────
Rappel Python + SQLite :
    import sqlite3
    conn = sqlite3.connect("fichier.db")   # crée le fichier s'il n'existe pas
    conn.row_factory = sqlite3.Row          # permet d'accéder aux colonnes par nom
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table WHERE col = ?", (valeur,))  # paramétré = anti-injection
    rows = cursor.fetchall()
    conn.commit()                           # écrire les changements
    conn.close()
"""

import sqlite3
import uuid
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "neurostep.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Retourne une connexion SQLite avec row_factory activé."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialise la base à partir de schema.sql (idempotent grâce à IF NOT EXISTS)."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
# APPLICATIONS
# ═══════════════════════════════════════════════════════════════════

def get_all_apps() -> list[dict]:
    """Retourne toutes les applications actives avec leurs fonctions cognitives."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.*,
               GROUP_CONCAT(fc.nom, ' · ') AS fonctions,
               GROUP_CONCAT(fc.id, ',')     AS fonctions_ids
        FROM applications a
        LEFT JOIN app_fonctions af ON af.app_id = a.id
        LEFT JOIN fonctions_cognitives fc ON fc.id = af.fonction_id
        WHERE a.statut = 'actif'
        GROUP BY a.id
        ORDER BY a.nom
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_app_by_id(app_id: int) -> dict | None:
    """Retourne une application par son ID avec fonctions et score moyen."""
    conn = get_connection()
    row = conn.execute("""
        SELECT a.*,
               GROUP_CONCAT(fc.nom, ' · ') AS fonctions,
               AVG(e.score_global)          AS score_moyen,
               COUNT(e.id)                  AS nb_evaluations
        FROM applications a
        LEFT JOIN app_fonctions af ON af.app_id = a.id
        LEFT JOIN fonctions_cognitives fc ON fc.id = af.fonction_id
        LEFT JOIN evaluations e ON e.app_id = a.id
        WHERE a.id = ?
        GROUP BY a.id
    """, (app_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_app(nom, description, objectif_ther="", plateforme="Non précisé",
               gratuit=1, prix_eur=None, url_store=None, editeur=None,
               langue="fr", fonction_ids=None) -> int:
    """Insère une application et ses liaisons fonctions cognitives."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO applications
            (nom, description, objectif_ther, plateforme, gratuit, prix_eur,
             url_store, editeur, langue)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nom, description, objectif_ther, plateforme, gratuit, prix_eur,
          url_store, editeur, langue))
    app_id = cursor.lastrowid

    if app_id and fonction_ids:
        for fid in fonction_ids:
            cursor.execute(
                "INSERT OR IGNORE INTO app_fonctions (app_id, fonction_id) VALUES (?, ?)",
                (app_id, fid)
            )
    conn.commit()
    conn.close()
    return app_id


def count_apps() -> int:
    conn = get_connection()
    n = conn.execute("SELECT COUNT(*) FROM applications WHERE statut='actif'").fetchone()[0]
    conn.close()
    return n


# ═══════════════════════════════════════════════════════════════════
# FONCTIONS COGNITIVES
# ═══════════════════════════════════════════════════════════════════

def get_all_fonctions() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM fonctions_cognitives ORDER BY categorie, nom"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_fonctions_for_app(app_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT fc.*, af.intensite
        FROM fonctions_cognitives fc
        JOIN app_fonctions af ON af.fonction_id = fc.id
        WHERE af.app_id = ?
        ORDER BY af.intensite, fc.nom
    """, (app_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_categories() -> list[str]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT categorie FROM fonctions_cognitives ORDER BY categorie"
    ).fetchall()
    conn.close()
    return [r["categorie"] for r in rows]


# ═══════════════════════════════════════════════════════════════════
# ÉVALUATIONS
# ═══════════════════════════════════════════════════════════════════

def get_evaluations_for_app(app_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM evaluations
        WHERE app_id = ?
        ORDER BY date_eval DESC
    """, (app_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_evaluation(app_id: int, evaluateur_type: str, score_global: int,
                   facilite_usage: int = None, pertinence_ther: int = None,
                   accessibilite: int = None, commentaire: str = "",
                   contexte_usage: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO evaluations
            (app_id, evaluateur_type, score_global, facilite_usage,
             pertinence_ther, accessibilite, commentaire, contexte_usage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (app_id, evaluateur_type, score_global, facilite_usage,
          pertinence_ther, accessibilite, commentaire, contexte_usage))
    eval_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return eval_id


# ═══════════════════════════════════════════════════════════════════
# PATIENTS
# ═══════════════════════════════════════════════════════════════════

def create_patient(alias: str = "", profil_lesionnel: str = "",
                   fonctions_atteintes: str = "",
                   notes_generales: str = "") -> str:
    """Crée un patient avec un UUID local (aucune donnée nominative)."""
    patient_id = str(uuid.uuid4())[:8].upper()
    conn = get_connection()
    conn.execute("""
        INSERT INTO patients (id, alias, profil_lesionnel, fonctions_atteintes, notes_generales)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_id, alias, profil_lesionnel, fonctions_atteintes, notes_generales))
    conn.commit()
    conn.close()
    return patient_id


def get_all_patients() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM patients ORDER BY date_creation DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_patient(patient_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ═══════════════════════════════════════════════════════════════════
# SUIVIS
# ═══════════════════════════════════════════════════════════════════

def add_suivi(patient_id: str, app_id: int, frequence: str = "",
              notes: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO suivis (patient_id, app_id, frequence, notes)
        VALUES (?, ?, ?, ?)
    """, (patient_id, app_id, frequence, notes))
    suivi_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return suivi_id


def get_suivis_for_patient(patient_id: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.*, a.nom AS app_nom, a.plateforme
        FROM suivis s
        JOIN applications a ON a.id = s.app_id
        WHERE s.patient_id = ?
        ORDER BY s.date_debut DESC
    """, (patient_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_suivi(suivi_id: int, statut: str = None,
                 progression: int = None, notes: str = None):
    conn = get_connection()
    updates = []
    params = []
    if statut is not None:
        updates.append("statut = ?")
        params.append(statut)
    if progression is not None:
        updates.append("progression = ?")
        params.append(progression)
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)
    if statut in ("terminé", "abandonné"):
        updates.append("date_fin = date('now')")

    if updates:
        params.append(suivi_id)
        conn.execute(
            f"UPDATE suivis SET {', '.join(updates)} WHERE id = ?", params
        )
        conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════════════

if not DB_PATH.exists():
    init_db()
