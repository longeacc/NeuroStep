"""Auth flow (register/verify/login/refresh/logout) + RBAC guards."""

from tests.conftest import (
    API,
    auth_header,
    login,
    register_verified,
    verify_token_for,
)


def test_register_then_login_blocked_until_verified(client):
    email = "unverified@x.fr"
    r = client.post(f"{API}/users/register", json={"email": email, "password": "secret1"})
    assert r.status_code == 201
    assert r.json()["is_verified"] is False
    # login blocked
    r = client.post(f"{API}/auth/login", data={"username": email, "password": "secret1"})
    assert r.status_code == 403
    # verify then login ok
    client.post(f"{API}/auth/verify-email?token={verify_token_for(email)}")
    r = client.post(f"{API}/auth/login", data={"username": email, "password": "secret1"})
    assert r.status_code == 200


def test_register_rejects_admin_role(client):
    r = client.post(
        f"{API}/users/register",
        json={"email": "wannabe@x.fr", "password": "secret1", "role": "admin"},
    )
    assert r.status_code == 422


def test_login_wrong_password(client):
    register_verified(client, "wp@x.fr")
    r = client.post(f"{API}/auth/login", data={"username": "wp@x.fr", "password": "nope"})
    assert r.status_code == 401


def test_verify_invalid_token(client):
    assert client.post(f"{API}/auth/verify-email?token=garbage").status_code == 400


def test_me_requires_auth(client):
    assert client.get(f"{API}/users/me").status_code == 401


def test_refresh_and_logout_cycle(client):
    register_verified(client, "cycle@x.fr")
    login(client, "cycle@x.fr")  # sets refresh cookie on the client
    r = client.post(f"{API}/auth/refresh")
    assert r.status_code == 200 and "access_token" in r.json()
    assert client.post(f"{API}/auth/logout").status_code == 204
    # refresh after logout fails
    assert client.post(f"{API}/auth/refresh").status_code == 401


def test_rbac_ergo_cannot_create_app(client, ergo_token):
    r = client.post(f"{API}/applications", json={"nom": "X"}, headers=auth_header(ergo_token))
    assert r.status_code == 403


def test_rbac_admin_can_crud_app(client, admin_token):
    r = client.post(
        f"{API}/applications",
        json={"nom": "Outil Test", "plateformes": ["Web"], "troubles": ["Aphasie"]},
        headers=auth_header(admin_token),
    )
    assert r.status_code == 201
    app_id = r.json()["id"]
    r = client.put(
        f"{API}/applications/{app_id}",
        json={"enrichi": True},
        headers=auth_header(admin_token),
    )
    assert r.status_code == 200 and r.json()["enrichi"] is True
