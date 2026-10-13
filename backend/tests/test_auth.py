import pytest
from flask.testing import FlaskClient
from flask import Flask
from app import db
from app.models import User
from sqlalchemy import text

MISSING = object()


def test_register_successed(client: FlaskClient):
    username = "test"
    email = "test@example.com"
    password = "test-password"
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["username"] == username and data["email"] == email
    assert "id" in data
    assert "password" not in data and "password_hash" not in data


@pytest.mark.parametrize("field", ["username", "email", "password"])
@pytest.mark.parametrize(
    "bad_value",
    [MISSING, "", "   ", 123],
    ids=["missing", "empty", "whitespace", "wrong_type"],
)
def test_register_rejects_bad_field(client: FlaskClient, field, bad_value):
    username = "test" if field != "username" else bad_value
    email = "test1@example.com" if field != "email" else bad_value
    password = "test-password" if field != "password" else bad_value

    payload = {"username": username, "email": email, "password": password}
    if bad_value is MISSING:
        del payload[field]

    response = client.post(
        "/auth/register",
        json=payload,
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "personal information cannot be empty"
    assert "password" not in data and "password_hash" not in data


@pytest.mark.parametrize("field", ["username", "email"])
def test_register_rejects_duplicate(client: FlaskClient, field):
    username = "test1"
    email = "test1@example.com"
    password = "test-password"
    client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )

    username = "test1" if field == "username" else "test2"
    email = "test1@example.com" if field == "email" else "test2@example.com"
    password = "test-password"
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )

    data = response.get_json()

    assert response.status_code == 409
    assert data["error"] == "username or email already taken"
    assert "password" not in data and "password_hash" not in data


def test_login_with_correct_pw(client: FlaskClient, registered_user: dict[str, str]):
    response = client.post("/auth/login", json=registered_user)

    data = response.get_json()

    assert response.status_code == 200
    assert "access_token" in data


@pytest.mark.parametrize("fields", ["email", "password"])
def test_login_with_wrong_fields(
    client: FlaskClient, registered_user: dict[str, str], fields
):
    registered_user[fields] = "wrong_val"

    response = client.post("/auth/login", json=registered_user)
    data = response.get_json()

    assert response.status_code == 401
    assert data["error"] == "invalid email or password"


@pytest.mark.parametrize("fields", ["email", "password"])
@pytest.mark.parametrize(
    "bad_value",
    [MISSING, "", "    ", 123],
    ids=["missing", "empty", "whitespace", "wrong_type"],
)
def test_login_with_empty_fields(
    client: FlaskClient, registered_user: dict[str, str], fields, bad_value
):

    if bad_value is MISSING:
        del registered_user[fields]
    else:
        registered_user[fields] = bad_value

    response = client.post("/auth/login", json=registered_user)

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "email or password cannot be empty"


def test_route_me_with_correct_auth(
    client: FlaskClient, registered_user: dict, auth_headers: dict
):
    response = client.get("/auth/me", headers=auth_headers)
    data = response.get_json()
    assert response.status_code == 200
    assert registered_user["id"] == data["id"]
    assert registered_user["username"] == data["username"]
    assert registered_user["email"] == data["email"]


def test_route_me_with_no_header(client: FlaskClient):
    response = client.get("/auth/me")
    data = response.get_json()
    assert response.status_code == 401
    assert data["error"] == "authentication required"


def test_route_me_with_invalid_auth(client: FlaskClient):
    response = client.get("/auth/me", headers={"Authorization": "Bearer invalidauth"})
    data = response.get_json()
    assert response.status_code == 401
    assert data["error"] == "invalid token"


def test_route_me_with_missing_user(
    app: Flask, client: FlaskClient, registered_user: dict, auth_headers: dict
):
    with app.app_context():
        user = db.session.get(User, registered_user["id"])
        db.session.delete(user)
        db.session.commit()

    response = client.get("/auth/me", headers=auth_headers)
    data = response.get_json()
    assert response.status_code == 401
    assert data["error"] == "the account doesn't exist"
