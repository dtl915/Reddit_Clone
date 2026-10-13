import pytest
from flask.testing import FlaskClient


def test_register_successed(client: FlaskClient):
    username = "test"
    email = "test@mail.com"
    password = "test-password"
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["username"] == username and data["email"] == email
    assert "ID" in data


def test_register_failed_empty_username(client: FlaskClient):
    email = "test@mail.com"
    password = "test-password"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "personal information cannot be empty"


def test_register_failed_empty_email(client: FlaskClient):
    username = "test"
    password = "test-password"
    response = client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "personal information cannot be empty"


def test_register_failed_empty_password(client: FlaskClient):
    username = "test"
    email = "test@mail.com"
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email},
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "personal information cannot be empty"


def test_register_with_repeated_username(client: FlaskClient):
    username = "test"
    email = "test1@mail.com"
    password = "test-password"
    client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )

    username = "test"
    email = "test2@mail.com"
    password = "test-password"
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )

    data = response.get_json()

    assert response.status_code == 409
    assert data["error"] == "username or email already taken"


def test_register_with_repeated_email(client: FlaskClient):
    username = "test1"
    email = "test@mail.com"
    password = "test-password"
    client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )

    username = "test2"
    email = "test@mail.com"
    password = "test-password"
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )

    data = response.get_json()

    assert response.status_code == 409
    assert data["error"] == "username or email already taken"
