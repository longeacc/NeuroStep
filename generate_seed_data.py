"""
generate_seed_data.py — Données de démonstration pour Neurostep
───────────────────────────────────────────────────────────────
20 applications fictives réalistes couvrant les 6 catégories cognitives.
Usage : python generate_seed_data.py
"""

import database as db

SEED_APPS = [
    # ── ATTENTION ────────────────────────────────────────────────
    {
        "nom": "AttentionBoost",
        "description": "Entraînement progressif de l'attention soutenue et sélective. "
                       "Exercices de détection de cibles, tâches de barrage adaptatives, "
                       "durée de session personnalisable. Statistiques de progression.",
        "objectif_ther": "Rééducation des fonctions attentionnelles post-AVC ou TCC",
        "plateforme": "iOS,Android",
        "gratuit": 1,
        "fonctions": ["Attention soutenue", "Attention sélective"],
    },
    {
        "nom": "DualTask Trainer",
        "description": "Application d'entraînement à l'attention divisée. Tâches duales "
                       "combinant traitement auditif et visuel. Niveaux de difficulté "
                       "progressifs calibrés sur les normes neuropsychologiques.",
        "objectif_ther": "Améliorer la capacité d'attention partagée en situation écologique",
        "plateforme": "iOS,Android,Web",
        "gratuit": 0,
        "prix_eur": 3.99,
        "fonctions": ["Attention divisée", "Attention soutenue"],
    },
    {
        "nom": "FocusZone",
        "description": "Jeu sérieux pour l'entraînement de la concentration. Environnements "
                       "immersifs avec distracteurs calibrés. Mesure du temps de réaction et "
                       "de la précision. Adapté aux adultes cérébrolésés.",
        "objectif_ther": "Renforcer l'attention sélective et la résistance aux distracteurs",
        "plateforme": "Android",
        "gratuit": 1,
        "fonctions": ["Attention sélective", "Inhibition"],
    },

    # ── MÉMOIRE ──────────────────────────────────────────────────
    {
        "nom": "MemoDay",
        "description": "Calendrier cognitif pour la mémoire prospective. Rappels contextuels "
                       "intelligents, simulation de tâches du quotidien (prise de médicaments, "
                       "rendez-vous, courses). Validation active par le patient.",
        "objectif_ther": "Compenser les troubles de mémoire prospective dans la vie quotidienne",
        "plateforme": "iOS,Android",
        "gratuit": 1,
        "fonctions": ["Mémoire prospective", "Planification"],
    },
    {
        "nom": "WorkMem Pro",
        "description": "Exercices de mémoire de travail : n-back visuel et auditif, empan "
                       "de chiffres, manipulation mentale de séquences. Difficulté adaptative. "
                       "Suivi des scores avec courbes de progression.",
        "objectif_ther": "Entraîner la mémoire de travail verbale et visuo-spatiale",
        "plateforme": "iOS,Android,Web",
        "gratuit": 1,
        "fonctions": ["Mémoire de travail", "Attention soutenue"],
    },
    {
        "nom": "SouvenirStory",
        "description": "Application de stimulation de la mémoire épisodique. Le patient "
                       "enregistre des événements de sa journée (photo + texte) et les "
                       "retrouve via des indices contextuels. Exercice de rappel différé.",
        "objectif_ther": "Soutenir l'encodage et la récupération en mémoire épisodique",
        "plateforme": "iOS",
        "gratuit": 0,
        "prix_eur": 5.99,
        "fonctions": ["Mémoire épisodique", "Mémoire sémantique"],
    },
    {
        "nom": "PilulierSmart",
        "description": "Gestionnaire de prise de médicaments avec rappels adaptés aux "
                       "troubles cognitifs. Interface épurée grands caractères. Confirmation "
                       "de prise obligatoire. Historique consultable par l'aidant ou l'ergo.",
        "objectif_ther": "Sécuriser l'observance thérapeutique chez le patient cérébrolésé",
        "plateforme": "iOS,Android",
        "gratuit": 1,
        "fonctions": ["Mémoire prospective"],
    },

    # ── FONCTIONS EXÉCUTIVES ─────────────────────────────────────
    {
        "nom": "PlanAction",
        "description": "Décomposition et séquençage des activités de la vie quotidienne. "
                       "L'ergothérapeute programme les tâches, le patient suit les étapes "
                       "visuelles. Chronomètre et auto-évaluation intégrés.",
        "objectif_ther": "Soutenir la planification et l'initiation des activités",
        "plateforme": "iOS,Android",
        "gratuit": 0,
        "prix_eur": 4.99,
        "fonctions": ["Planification", "Flexibilité cognitive"],
    },
    {
        "nom": "InhibiGo",
        "description": "Tâches d'inhibition de réponse : stop-signal, go/no-go, Stroop "
                       "simplifié. Mesure des temps de réaction et taux d'erreurs. "
                       "Adapté TCC légers à modérés.",
        "objectif_ther": "Améliorer le contrôle inhibiteur post-traumatique",
        "plateforme": "Android,Web",
        "gratuit": 1,
        "fonctions": ["Inhibition", "Attention sélective"],
    },
    {
        "nom": "FlexMind",
        "description": "Jeux de flexibilité cognitive : tri de cartes avec changement "
                       "de règle, catégorisation alternée, tâche de switch. Interface "
                       "ludique adaptée aux syndromes dysexécutifs.",
        "objectif_ther": "Entraîner la flexibilité mentale et la mise à jour en mémoire",
        "plateforme": "Web",
        "gratuit": 1,
        "fonctions": ["Flexibilité cognitive", "Mémoire de travail"],
    },
    {
        "nom": "Problemo",
        "description": "Scénarios de résolution de problèmes du quotidien : gérer un budget, "
                       "organiser un trajet, préparer un repas. Guidage progressif avec "
                       "feedback immédiat sur les stratégies utilisées.",
        "objectif_ther": "Développer les stratégies de résolution de problèmes écologiques",
        "plateforme": "iOS,Android",
        "gratuit": 1,
        "fonctions": ["Résolution de problèmes", "Planification"],
    },

    # ── LANGAGE ──────────────────────────────────────────────────
    {
        "nom": "LexiCog",
        "description": "Remédiation du langage oral et écrit pour patients aphasiques. "
                       "Exercices de dénomination, compréhension orale de consignes, "
                       "appariement mot-image. Banque de 3000 stimuli calibrés.",
        "objectif_ther": "Rééducation des troubles du langage acquis post-AVC",
        "plateforme": "iOS,Android",
        "gratuit": 1,
        "fonctions": ["Compréhension orale", "Expression orale", "Lecture"],
    },
    {
        "nom": "LecturePlus",
        "description": "Entraînement à la lecture fonctionnelle : lecture de menus, "
                       "d'horaires de bus, de notices de médicaments. Taille de police "
                       "et contraste ajustables. Synthèse vocale intégrée.",
        "objectif_ther": "Retrouver une autonomie de lecture dans les activités quotidiennes",
        "plateforme": "iOS,Android",
        "gratuit": 0,
        "prix_eur": 2.99,
        "fonctions": ["Lecture", "Compréhension orale"],
    },
    {
        "nom": "ÉcriVite",
        "description": "Outil d'aide à l'écriture avec prédiction de mots adaptée "
                       "aux patients dysorthographiques. Clavier simplifié, dictée vocale "
                       "avec correction assistée, bibliothèque de phrases-types.",
        "objectif_ther": "Compenser les troubles de l'écriture fonctionnelle",
        "plateforme": "iOS,Android",
        "gratuit": 1,
        "fonctions": ["Écriture", "Expression orale"],
    },

    # ── VISUO-SPATIAL ────────────────────────────────────────────
    {
        "nom": "VisuoSpace",
        "description": "Exercices de perception visuo-spatiale : reconnaissance de formes "
                       "dans des fonds complexes, rotation mentale, reconstruction de puzzles "
                       "3D. Progression de la simple détection à la manipulation mentale.",
        "objectif_ther": "Rééducation des troubles visuo-spatiaux et de la négligence",
        "plateforme": "iPad",
        "gratuit": 0,
        "prix_eur": 9.99,
        "fonctions": ["Perception visuelle", "Orientation spatiale"],
    },
    {
        "nom": "NaviCog",
        "description": "Application de navigation simplifiée avec guidage cognitif adapté. "
                       "Instructions pas à pas avec repères visuels saillants. Entraînement "
                       "à l'orientation dans des environnements familiers et nouveaux.",
        "objectif_ther": "Améliorer l'orientation spatiale en contexte de déplacement réel",
        "plateforme": "iOS,Android",
        "gratuit": 1,
        "fonctions": ["Orientation spatiale", "Mémoire de travail"],
    },

    # ── PRAXIES ──────────────────────────────────────────────────
    {
        "nom": "GestuGuide",
        "description": "Vidéos de démonstration de gestes du quotidien (habillage, cuisine, "
                       "hygiène) avec décomposition en sous-étapes. Le patient peut filmer "
                       "sa propre exécution et la comparer au modèle.",
        "objectif_ther": "Rééducation des praxies idéomotrices et de l'habillage",
        "plateforme": "iOS,Android",
        "gratuit": 1,
        "fonctions": ["Praxies gestuelles", "Planification"],
    },
    {
        "nom": "ConstructoPuzzle",
        "description": "Puzzles et tangrams numériques de difficulté croissante. "
                       "Manipulation tactile d'objets 2D et 3D. Feedback visuel immédiat "
                       "sur le placement des pièces.",
        "objectif_ther": "Entraîner les praxies constructives et les capacités visuo-spatiales",
        "plateforme": "iPad,Android",
        "gratuit": 1,
        "fonctions": ["Praxies constructives", "Perception visuelle"],
    },

    # ── MULTI-DOMAINE ────────────────────────────────────────────
    {
        "nom": "CogniDaily",
        "description": "Programme complet de remédiation cognitive quotidien. 15 minutes "
                       "par jour couvrant attention, mémoire et fonctions exécutives. "
                       "Algorithme adaptatif ajustant la difficulté en temps réel. "
                       "Rapport hebdomadaire envoyé à l'ergothérapeute.",
        "objectif_ther": "Maintien et stimulation cognitive globale post-lésion cérébrale",
        "plateforme": "iOS,Android,Web",
        "gratuit": 0,
        "prix_eur": 7.99,
        "fonctions": ["Attention soutenue", "Mémoire de travail", "Planification",
                       "Flexibilité cognitive"],
    },
    {
        "nom": "NeuroCoach",
        "description": "Assistant virtuel de remédiation cognitive avec exercices "
                       "personnalisés selon le bilan neuropsychologique du patient. "
                       "Interface patient + interface ergothérapeute séparées. "
                       "Gamification et système de récompenses.",
        "objectif_ther": "Programme intégré de rééducation cognitive avec suivi professionnel",
        "plateforme": "iOS,Android",
        "gratuit": 0,
        "prix_eur": 12.99,
        "fonctions": ["Attention soutenue", "Mémoire de travail", "Inhibition",
                       "Mémoire prospective"],
    },
]


def seed():
    """Insère les applications de démonstration."""
    db.init_db()
    fonctions = db.get_all_fonctions()
    fn_map = {f["nom"]: f["id"] for f in fonctions}

    inserted = 0
    for app in SEED_APPS:
        fn_ids = [fn_map[fn] for fn in app.get("fonctions", []) if fn in fn_map]
        app_id = db.insert_app(
            nom=app["nom"],
            description=app["description"],
            objectif_ther=app.get("objectif_ther", ""),
            plateforme=app.get("plateforme", "Non précisé"),
            gratuit=app.get("gratuit", 1),
            prix_eur=app.get("prix_eur"),
            fonction_ids=fn_ids,
        )
        if app_id:
            inserted += 1

    # Ajouter quelques évaluations de démonstration
    _seed_evaluations()
    print(f"✅ {inserted} applications + évaluations insérées.")


def _seed_evaluations():
    """Quelques évaluations fictives pour la démo."""
    evals = [
        (1, "ergo", 5, 4, 5, 4, "Très efficace pour les patients TCC léger avec troubles attentionnels."),
        (1, "ergo", 4, 5, 4, 3, "Bonne interface, progression bien calibrée."),
        (1, "patient", 4, 5, 4, 4, "Facile à utiliser, je vois des progrès."),
        (4, "ergo", 5, 5, 5, 5, "Indispensable pour mes patients avec oublis prospectifs."),
        (4, "patient", 4, 4, 4, 4, "Les rappels sont vraiment utiles au quotidien."),
        (5, "ergo", 4, 3, 5, 3, "Bon n-back mais interface un peu complexe pour certains patients."),
        (8, "ergo", 5, 4, 5, 4, "Excellent pour le séquençage des tâches domestiques."),
        (9, "ergo", 4, 4, 4, 4, "Go/no-go bien adapté, progression satisfaisante."),
        (12, "ergo", 5, 4, 5, 5, "Banque de stimuli très complète pour l'aphasie."),
        (19, "ergo", 4, 3, 4, 3, "Programme complet mais prix élevé pour les patients."),
    ]
    for app_id, etype, sg, fu, pt, acc, comment in evals:
        try:
            db.add_evaluation(app_id, etype, sg, fu, pt, acc, comment)
        except Exception:
            pass


if __name__ == "__main__":
    seed()
