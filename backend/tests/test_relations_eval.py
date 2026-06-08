"""Therapeutic relations (cloisonnement) + evaluations."""

from tests.conftest import API, auth_header, login, register_verified


def _patient_id(client, email):
    register_verified(client, email, role="patient")
    tok = login(client, email)
    return client.get(f"{API}/users/me", headers=auth_header(tok)).json()["id"]


def test_relation_lifecycle(client, ergo_token):
    pid = _patient_id(client, "pat_rel@x.fr")
    # create
    r = client.post(f"{API}/relations", json={"patient_id": pid}, headers=auth_header(ergo_token))
    assert r.status_code == 201
    assert r.json()["active"] is True
    # list
    rels = client.get(f"{API}/relations", headers=auth_header(ergo_token)).json()
    assert any(rel["patient_id"] == pid for rel in rels)
    # end (soft deactivate)
    assert client.delete(f"{API}/relations/{pid}", headers=auth_header(ergo_token)).status_code == 204


def test_relation_unknown_patient(client, ergo_token):
    r = client.post(f"{API}/relations", json={"patient_id": 999999}, headers=auth_header(ergo_token))
    assert r.status_code == 404


def test_relation_requires_ergo(client, admin_token):
    # admin is not an ergo -> 403 on ergo-only endpoint
    r = client.post(f"{API}/relations", json={"patient_id": 1}, headers=auth_header(admin_token))
    assert r.status_code == 403


EVAL_PAYLOAD = {
    "pertinence_clinique": 4,
    "utilisabilite": 5,
    "efficacite": 4,
    "accessibilite": 3,
    "integration": 5,
    "avantages": "Simple à prendre en main",
    "limites": "Voix robotique",
    "contexte_utilisation": "Séances de rééducation",
    "profil_patient": "Aphasie modérée",
}


def test_evaluation_create_list_summary(client, ergo_token):
    app_id = client.get(f"{API}/applications").json()[0]["id"]
    r = client.post(
        f"{API}/evaluations",
        json={"application_id": app_id, **EVAL_PAYLOAD},
        headers=auth_header(ergo_token),
    )
    assert r.status_code == 201
    body = r.json()
    assert body["moyenne"] == 4.2  # (4+5+4+3+5)/5
    assert body["auteur_rpps_verifie"] is False

    evals = client.get(f"{API}/evaluations/application/{app_id}").json()
    assert any(e["pertinence_clinique"] == 4 for e in evals)

    summary = client.get(f"{API}/evaluations/application/{app_id}/summary").json()
    assert summary["nombre"] >= 1
    assert "efficacite" in summary["moyennes_par_axe"]
    assert summary["moyenne_globale"] is not None


def test_evaluation_axis_out_of_range(client, ergo_token):
    app_id = client.get(f"{API}/applications").json()[0]["id"]
    bad = {**EVAL_PAYLOAD, "pertinence_clinique": 6}
    r = client.post(
        f"{API}/evaluations",
        json={"application_id": app_id, **bad},
        headers=auth_header(ergo_token),
    )
    assert r.status_code == 422


def test_evaluation_unknown_app(client, ergo_token):
    r = client.post(
        f"{API}/evaluations",
        json={"application_id": 999999, **EVAL_PAYLOAD},
        headers=auth_header(ergo_token),
    )
    assert r.status_code == 404
