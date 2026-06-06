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


def test_evaluation_create_and_list(client, ergo_token):
    app_id = client.get(f"{API}/applications").json()[0]["id"]
    r = client.post(
        f"{API}/evaluations",
        json={"application_id": app_id, "rating": 4, "comment": "utile"},
        headers=auth_header(ergo_token),
    )
    assert r.status_code == 201
    evals = client.get(f"{API}/evaluations/application/{app_id}").json()
    assert any(e["rating"] == 4 for e in evals)


def test_evaluation_unknown_app(client, ergo_token):
    r = client.post(
        f"{API}/evaluations",
        json={"application_id": 999999, "rating": 3},
        headers=auth_header(ergo_token),
    )
    assert r.status_code == 404
