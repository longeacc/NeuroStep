"""
search_engine.py — Moteur de recherche pour Neurostep
─────────────────────────────────────────────────────
Mode 1 (par défaut) : sentence-transformers (embedding sémantique 384 dims)
Mode 2 (fallback)   : TF-IDF + cosine_similarity (si modèle non disponible)

Le mode est détecté automatiquement au premier appel.
"""

import os
import re
import pickle
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

import database as db

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDINGS_PATH = Path(__file__).parent / "embeddings.pkl"

_model = None
_use_tfidf = False
_tfidf_vectorizer = None
_cache = None  # (app_ids, matrix)


def _try_load_model():
    """Tente de charger sentence-transformers, sinon bascule en TF-IDF."""
    global _model, _use_tfidf
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
        _use_tfidf = False
        print(f"✅ Modèle sémantique chargé : {MODEL_NAME} ({_model.get_sentence_embedding_dimension()} dims)")
    except Exception as e:
        _use_tfidf = True
        print(f"⚠️  Modèle sémantique indisponible ({e.__class__.__name__}). Fallback TF-IDF activé.")


def _get_model():
    global _model, _use_tfidf
    if _model is None and not _use_tfidf:
        _try_load_model()
    return _model


def _build_text(app: dict) -> str:
    """Concatène les champs pertinents pour l'indexation."""
    parts = [
        app.get("nom", ""),
        app.get("description", ""),
        app.get("objectif_ther", "") or "",
        app.get("fonctions", "") or "",
    ]
    return " ".join(p for p in parts if p).strip()


def _normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return matrix / norms


def build_index(force: bool = False) -> tuple[list[int], np.ndarray]:
    """Construit l'index (embeddings ou TF-IDF selon le mode)."""
    global _cache, _tfidf_vectorizer, _use_tfidf

    # Vérifier le cache
    db_mtime = os.path.getmtime(db.DB_PATH) if db.DB_PATH.exists() else 0
    emb_mtime = os.path.getmtime(EMBEDDINGS_PATH) if EMBEDDINGS_PATH.exists() else 0

    if not force and _cache is not None:
        return _cache
    if not force and EMBEDDINGS_PATH.exists() and emb_mtime >= db_mtime:
        with open(EMBEDDINGS_PATH, "rb") as f:
            _cache = pickle.load(f)
        return _cache

    apps = db.get_all_apps()
    if not apps:
        _cache = ([], np.zeros((0, 100)))
        return _cache

    texts = [_build_text(a) for a in apps]
    app_ids = [a["id"] for a in apps]

    model = _get_model()

    if not _use_tfidf and model is not None:
        # Mode sémantique
        matrix = model.encode(texts, show_progress_bar=False, batch_size=32)
        matrix = _normalize(matrix)
    else:
        # Mode TF-IDF fallback
        _tfidf_vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            sublinear_tf=True,
            strip_accents="unicode",
        )
        matrix = _tfidf_vectorizer.fit_transform(texts).toarray()
        matrix = _normalize(matrix)

    _cache = (app_ids, matrix)

    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump((_cache, _use_tfidf), f)

    return _cache


def _encode_query(query: str) -> np.ndarray:
    """Encode la requête dans le même espace que l'index."""
    global _use_tfidf

    if not _use_tfidf and _model is not None:
        vec = _model.encode([query])
    elif _tfidf_vectorizer is not None:
        vec = _tfidf_vectorizer.transform([query]).toarray()
    else:
        # Fallback minimal si rien n'est prêt
        build_index()
        return _encode_query(query)

    return _normalize(vec)


def search(query: str, k: int = 10,
           plateforme: str = None,
           gratuit_only: bool = False,
           fonction_id: int = None) -> list[dict]:
    """
    Recherche par similarité (sémantique ou TF-IDF).
    Retourne top-k résultats avec score_pct.
    """
    app_ids, matrix = build_index()

    if not app_ids or matrix.size == 0:
        return []

    q_vec = _encode_query(query)
    scores = cosine_similarity(q_vec, matrix)[0]

    # Assemblage avec métadonnées
    results = []
    conn = db.get_connection()

    for idx, app_id in enumerate(app_ids):
        row = conn.execute("""
            SELECT a.*,
                   GROUP_CONCAT(fc.nom, ' · ') AS fonctions,
                   AVG(e.score_global) AS score_moyen,
                   COUNT(e.id) AS nb_evaluations
            FROM applications a
            LEFT JOIN app_fonctions af ON af.app_id = a.id
            LEFT JOIN fonctions_cognitives fc ON fc.id = af.fonction_id
            LEFT JOIN evaluations e ON e.app_id = a.id
            WHERE a.id = ?
            GROUP BY a.id
        """, (app_id,)).fetchone()

        if not row:
            continue
        r = dict(row)

        # Filtres
        if plateforme and plateforme != "Toutes":
            if plateforme.lower() not in r["plateforme"].lower():
                continue
        if gratuit_only and not r["gratuit"]:
            continue
        if fonction_id:
            fn_check = conn.execute(
                "SELECT 1 FROM app_fonctions WHERE app_id=? AND fonction_id=?",
                (app_id, fonction_id)
            ).fetchone()
            if not fn_check:
                continue

        r["score_sim"] = float(scores[idx])
        r["score_pct"] = round(float(scores[idx]) * 100, 1)
        results.append(r)

    conn.close()
    results.sort(key=lambda x: x["score_sim"], reverse=True)
    return results[:k]


def explain_match(query: str, description: str) -> dict:
    """Identifie la phrase de la description la plus proche de la requête."""
    sentences = [s.strip() for s in description.replace("\n", ".").split(".")
                 if len(s.strip()) > 10]
    if not sentences:
        return {"best_sentence": description[:120], "score": 0.0}

    if not _use_tfidf and _model is not None:
        q_vec = _model.encode([query])
        s_vecs = _model.encode(sentences)
        scores = cosine_similarity(q_vec, s_vecs)[0]
    elif _tfidf_vectorizer is not None:
        # TF-IDF local sur les phrases
        local_tfidf = TfidfVectorizer(
            ngram_range=(1, 2), sublinear_tf=True, strip_accents="unicode"
        )
        try:
            s_vecs = local_tfidf.fit_transform(sentences).toarray()
            q_vec = local_tfidf.transform([query]).toarray()
            scores = cosine_similarity(q_vec, s_vecs)[0]
        except Exception:
            return {"best_sentence": sentences[0], "score": 0.5}
    else:
        return {"best_sentence": sentences[0], "score": 0.5}

    best_idx = int(np.argmax(scores))
    return {
        "best_sentence": sentences[best_idx],
        "score": float(scores[best_idx]),
    }


def get_mode() -> str:
    """Retourne le mode actif pour affichage dans l'UI."""
    _get_model()  # trigger la détection
    return "TF-IDF (fallback)" if _use_tfidf else f"Sémantique ({MODEL_NAME})"
