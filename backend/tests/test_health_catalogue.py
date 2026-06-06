"""Health, catalogue listing, filtering, search, taxonomy meta."""

from tests.conftest import API


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_applications(client):
    r = client.get(f"{API}/applications")
    assert r.status_code == 200
    apps = r.json()
    # 15 migrés depuis le JSON legacy (d'autres tests peuvent en ajouter).
    assert len(apps) >= 15
    # nested taxonomy is exposed
    assert "troubles" in apps[0] and "themes" in apps[0]


def test_filter_by_os(client):
    r = client.get(f"{API}/applications", params={"os": "Web"})
    assert r.status_code == 200
    for app in r.json():
        assert "Web" in app["plateformes"]


def test_filter_by_trouble(client):
    r = client.get(f"{API}/applications", params={"trouble": "Aphasie"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_text_search(client):
    r = client.get(f"{API}/applications", params={"q": "voix"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_application_detail_and_404(client):
    first = client.get(f"{API}/applications").json()[0]
    r = client.get(f"{API}/applications/{first['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == first["id"]
    assert client.get(f"{API}/applications/999999").status_code == 404


def test_meta_endpoints(client):
    assert client.get(f"{API}/applications/_meta/troubles").status_code == 200
    assert client.get(f"{API}/applications/_meta/themes").status_code == 200
    fonctions = client.get(f"{API}/applications/_meta/fonctions").json()
    assert len(fonctions) == 5
    noms = {f["nom"] for f in fonctions}
    assert "Compensation motrice" in noms
