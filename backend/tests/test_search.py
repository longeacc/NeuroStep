"""Recherche multi-critères enrichie (spec 5.3)."""

from tests.conftest import API


def test_search_text(client):
    r = client.get(f"{API}/applications/search", params={"q": "voix"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_search_by_fonction_cognitive(client):
    r = client.get(f"{API}/applications/search", params={"fonction": "Attention"})
    assert r.status_code == 200
    apps = r.json()
    assert len(apps) >= 1
    # chaque app retournée cible au moins un trouble rattaché à "Attention"
    for app in apps:
        assert any(
            t["fonction"] and t["fonction"]["nom"] == "Attention" for t in app["troubles"]
        )


def test_search_gratuit(client):
    r = client.get(f"{API}/applications/search", params={"gratuit": "true"})
    assert r.status_code == 200
    assert all(app["gratuit"] for app in r.json())


def test_search_plateformes_overlap(client):
    r = client.get(
        f"{API}/applications/search", params=[("plateformes", "Web"), ("plateformes", "iOS")]
    )
    assert r.status_code == 200
    for app in r.json():
        assert {"Web", "iOS"} & set(app["plateformes"])


def test_search_objectif(client):
    # objectif_ther contient souvent "Communication" dans le jeu de données
    r = client.get(f"{API}/applications/search", params={"objectif": "communication"})
    assert r.status_code == 200


def test_search_by_sous_fonction(client):
    r = client.get(f"{API}/applications/search", params={"sous_fonction": "Réception"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_search_by_retentissement(client):
    """Insère un retentissement lié à un trouble, puis filtre dessus."""
    from app.db.session import SessionLocal
    from app.models.cognition import RetentissementVieQuotidienne
    from app.models.taxonomy import Trouble
    from sqlalchemy import select

    libelle = "Ne peut pas suivre une procédure écrite"
    with SessionLocal() as db:
        ret = db.scalar(
            select(RetentissementVieQuotidienne).where(
                RetentissementVieQuotidienne.libelle == libelle
            )
        )
        if ret is None:
            ret = RetentissementVieQuotidienne(libelle=libelle)
            db.add(ret)
            db.flush()
        trouble = db.scalar(
            select(Trouble).where(Trouble.name == "Trouble de la compréhension")
        )
        if ret not in trouble.retentissements:
            trouble.retentissements.append(ret)
        db.commit()

    # exposé via le meta endpoint
    metas = client.get(f"{API}/applications/_meta/retentissements").json()
    assert any(m["libelle"] == libelle for m in metas)

    r = client.get(f"{API}/applications/search", params={"retentissement": libelle})
    assert r.status_code == 200
    apps = r.json()
    assert len(apps) >= 1
    for app in apps:
        assert any(t["name"] == "Trouble de la compréhension" for t in app["troubles"])
