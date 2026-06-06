"""L'ADAPT mapping correctness (spec 4.5.2)."""

from tests.conftest import API


def _troubles_by_name(client):
    return {t["name"]: t for t in client.get(f"{API}/applications/_meta/troubles").json()}


def test_all_troubles_mapped(client):
    troubles = _troubles_by_name(client)
    assert len(troubles) == 9
    for t in troubles.values():
        if t["name"] != "Hémiplégie":
            assert t["fonction"] is not None, t["name"]


def test_aphasie_mapping(client):
    aphasie = _troubles_by_name(client)["Aphasie"]
    assert aphasie["fonction"]["nom"] == "Langage oral"
    assert {s["nom"] for s in aphasie["sous_fonctions"]} == {"Production", "Réception"}


def test_hemiplegie_is_motor(client):
    h = _troubles_by_name(client)["Hémiplégie"]
    assert h["fonction"]["nom"] == "Compensation motrice"
    assert h["fonction"]["is_motrice"] is True


def test_memoire_subfunctions(client):
    m = _troubles_by_name(client)["Troubles mnésiques"]
    assert {s["nom"] for s in m["sous_fonctions"]} == {
        "Encodage",
        "Stockage",
        "Récupération",
    }
