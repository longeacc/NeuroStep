"""L'ADAPT taxonomy reference data (spec 4.5.2).

Derived from the mapping table in the spec. The full L'ADAPT PDF defines additional
cognitive domains (target: 7); only the 5 needed by the current trouble set are
encoded here — extend `LADAPT_FONCTIONS` + `TROUBLE_MAPPING` as more are sourced.
"""

# Cognitive function -> {motor flag, full list of sub-functions}.
LADAPT_FONCTIONS: dict[str, dict] = {
    "Langage oral": {
        "is_motrice": False,
        "sous_fonctions": ["Production", "Réception"],
    },
    "Mémoire épisodique": {
        "is_motrice": False,
        "sous_fonctions": ["Encodage", "Stockage", "Récupération"],
    },
    "Attention": {
        "is_motrice": False,
        "sous_fonctions": [
            "Sélective",
            "Soutenue",
            "Attention divisée",
            "Vitesse de traitement",
        ],
    },
    "Gnosies visuelles": {
        "is_motrice": False,
        "sous_fonctions": ["Visuospatiale", "Visuoconstruction"],
    },
    # Motor, not cognitive — kept because some tools compensate motor deficits.
    "Compensation motrice": {"is_motrice": True, "sous_fonctions": []},
}

# Legacy trouble label -> (cognitive function, [sub-functions]).
TROUBLE_MAPPING: dict[str, tuple[str, list[str]]] = {
    "Trouble du langage": ("Langage oral", ["Production"]),
    "Aphasie": ("Langage oral", ["Production", "Réception"]),
    "Trouble de la compréhension": ("Langage oral", ["Réception"]),
    "Troubles mnésiques": (
        "Mémoire épisodique",
        ["Encodage", "Stockage", "Récupération"],
    ),
    "Troubles de l'attention": ("Attention", ["Sélective", "Soutenue"]),
    "Fatigabilité modérée": (
        "Attention",
        ["Attention divisée", "Vitesse de traitement"],
    ),
    "Problème d'orientation": ("Gnosies visuelles", ["Visuospatiale"]),
    "Problème visuo-spatial": (
        "Gnosies visuelles",
        ["Visuospatiale", "Visuoconstruction"],
    ),
    "Hémiplégie": ("Compensation motrice", []),
}
