"""Prescription numérique : workflow ergo + patient, PDF, lien sécurisé (spec 5.4)."""

from tests.conftest import API, auth_header, login, register_verified


def _patient_id(client, email):
    register_verified(client, email, role="patient")
    tok = login(client, email)
    return client.get(f"{API}/users/me", headers=auth_header(tok)).json()["id"]


def _ergo_with_patient(client, ergo_email, patient_email):
    """Crée un ergo + un patient liés par une relation active."""
    register_verified(client, ergo_email, role="ergo")
    ergo_tok = login(client, ergo_email)
    pid = _patient_id(client, patient_email)
    client.post(f"{API}/relations", json={"patient_id": pid}, headers=auth_header(ergo_tok))
    return ergo_tok, pid


def test_prescription_requires_active_relation(client):
    """Sans relation thérapeutique active -> 403 (cloisonnement)."""
    register_verified(client, "ergo_norel@x.fr", role="ergo")
    ergo_tok = login(client, "ergo_norel@x.fr")
    pid = _patient_id(client, "pat_norel@x.fr")
    app_id = client.get(f"{API}/applications").json()[0]["id"]
    r = client.post(
        f"{API}/prescriptions",
        json={"patient_id": pid, "items": [{"application_id": app_id, "priorite": 1}]},
        headers=auth_header(ergo_tok),
    )
    assert r.status_code == 403


def test_full_prescription_workflow(client):
    ergo_tok, pid = _ergo_with_patient(client, "ergo_presc@x.fr", "pat_presc@x.fr")
    apps = client.get(f"{API}/applications").json()
    a1, a2 = apps[0]["id"], apps[1]["id"]

    # 1. création (brouillon)
    r = client.post(
        f"{API}/prescriptions",
        json={
            "patient_id": pid,
            "notes": "Programme de 4 semaines",
            "items": [
                {"application_id": a1, "consignes": "Séances de 20 min", "priorite": 1},
                {"application_id": a2, "priorite": 2},
            ],
        },
        headers=auth_header(ergo_tok),
    )
    assert r.status_code == 201, r.text
    presc = r.json()
    assert presc["status"] == "draft"
    assert len(presc["items"]) == 2
    presc_id = presc["id"]

    # 2. PDF refusé tant que non validé
    assert (
        client.get(f"{API}/prescriptions/{presc_id}/pdf", headers=auth_header(ergo_tok)).status_code
        == 409
    )

    # 3. validation -> token de partage
    r = client.post(f"{API}/prescriptions/{presc_id}/validate", headers=auth_header(ergo_tok))
    assert r.status_code == 200
    token = r.json()["share_token"]
    assert token

    # 4. PDF généré (reportlab)
    pdf = client.get(f"{API}/prescriptions/{presc_id}/pdf", headers=auth_header(ergo_tok))
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content[:4] == b"%PDF"

    # 5. accès patient via lien sécurisé (sans auth)
    shared = client.get(f"{API}/prescriptions/shared/{token}")
    assert shared.status_code == 200
    item_id = shared.json()["items"][0]["id"]

    # 6. feedback patient
    fb = client.post(
        f"{API}/prescriptions/shared/{token}/items/{item_id}/feedback",
        json={"feedback": "Outil utilisé tous les jours"},
    )
    assert fb.status_code == 200

    # le feedback est bien enregistré
    again = client.get(f"{API}/prescriptions/shared/{token}").json()
    assert any(i["feedback_patient"] for i in again["items"])


def test_shared_invalid_token(client):
    assert client.get(f"{API}/prescriptions/shared/inexistant").status_code == 404


def test_prescription_my_list(client):
    ergo_tok, pid = _ergo_with_patient(client, "ergo_list@x.fr", "pat_list@x.fr")
    app_id = client.get(f"{API}/applications").json()[0]["id"]
    client.post(
        f"{API}/prescriptions",
        json={"patient_id": pid, "items": [{"application_id": app_id}]},
        headers=auth_header(ergo_tok),
    )
    mine = client.get(f"{API}/prescriptions", headers=auth_header(ergo_tok)).json()
    assert len(mine) >= 1
