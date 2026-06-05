-- schema.sql — Neurostep database schema
-- SQLite3 — toutes les données restent en local (RGPD-by-design)

CREATE TABLE IF NOT EXISTS applications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT    NOT NULL UNIQUE,
    description     TEXT    NOT NULL,
    objectif_ther   TEXT,
    plateforme      TEXT    NOT NULL DEFAULT 'Non précisé',
    gratuit         INTEGER NOT NULL DEFAULT 1,
    prix_eur        REAL,
    url_store       TEXT,
    editeur         TEXT,
    langue          TEXT    DEFAULT 'fr',
    date_ajout      TEXT    DEFAULT (date('now')),
    statut          TEXT    DEFAULT 'actif'
);

CREATE TABLE IF NOT EXISTS fonctions_cognitives (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL UNIQUE,
    categorie   TEXT NOT NULL,
    description TEXT,
    exemples    TEXT
);

CREATE TABLE IF NOT EXISTS app_fonctions (
    app_id      INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    fonction_id INTEGER NOT NULL REFERENCES fonctions_cognitives(id) ON DELETE CASCADE,
    intensite   TEXT DEFAULT 'principale',
    PRIMARY KEY (app_id, fonction_id)
);

CREATE TABLE IF NOT EXISTS evaluations (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    app_id           INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    evaluateur_type  TEXT NOT NULL DEFAULT 'ergo',
    score_global     INTEGER NOT NULL,
    facilite_usage   INTEGER,
    pertinence_ther  INTEGER,
    accessibilite    INTEGER,
    commentaire      TEXT,
    date_eval        TEXT DEFAULT (datetime('now')),
    contexte_usage   TEXT
);

CREATE TABLE IF NOT EXISTS patients (
    id                  TEXT PRIMARY KEY,
    alias               TEXT,
    date_creation       TEXT DEFAULT (date('now')),
    profil_lesionnel    TEXT,
    fonctions_atteintes TEXT,
    notes_generales     TEXT
);

CREATE TABLE IF NOT EXISTS suivis (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id      TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    app_id          INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    date_debut      TEXT DEFAULT (date('now')),
    date_fin        TEXT,
    statut          TEXT DEFAULT 'en_cours',
    frequence       TEXT,
    progression     INTEGER,
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_eval_app ON evaluations(app_id);
CREATE INDEX IF NOT EXISTS idx_af_app ON app_fonctions(app_id);
CREATE INDEX IF NOT EXISTS idx_suivi_patient ON suivis(patient_id);

INSERT OR IGNORE INTO fonctions_cognitives (nom, categorie, description) VALUES
('Attention soutenue',    'attention',     'Maintien de la concentration sur une tâche prolongée'),
('Attention sélective',   'attention',     'Filtrage des distracteurs, focalisation sur le stimulus cible'),
('Attention divisée',     'attention',     'Traitement simultané de deux sources d''information'),
('Mémoire de travail',    'mémoire',       'Rétention et manipulation d''informations à court terme'),
('Mémoire prospective',   'mémoire',       'Souvenir de réaliser une action future planifiée'),
('Mémoire épisodique',    'mémoire',       'Rappel d''événements personnellement vécus'),
('Mémoire sémantique',    'mémoire',       'Connaissances générales sur le monde'),
('Planification',         'exécutif',      'Anticipation et organisation des étapes d''une action'),
('Inhibition',            'exécutif',      'Suppression des réponses automatiques inadaptées'),
('Flexibilité cognitive', 'exécutif',      'Alternance entre règles ou points de vue différents'),
('Résolution de problèmes','exécutif',     'Stratégies adaptatives face à des obstacles'),
('Compréhension orale',   'langage',       'Décodage du langage parlé'),
('Expression orale',      'langage',       'Production de discours cohérent'),
('Lecture',               'langage',       'Décodage et compréhension de l''écrit'),
('Écriture',              'langage',       'Production graphique et orthographique'),
('Perception visuelle',   'visuo-spatial', 'Reconnaissance de formes, couleurs, objets'),
('Orientation spatiale',  'visuo-spatial', 'Représentation et navigation dans l''espace'),
('Praxies gestuelles',    'praxies',       'Exécution de gestes sur commande ou imitation'),
('Praxies constructives', 'praxies',       'Assemblage d''éléments en un tout cohérent');
