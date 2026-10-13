import pytest
from flask.testing import FlaskClient

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
    assert "ID" in data
    assert "password" not in data and "password_hash" not in data


@pytest.mark.parametrize("field", ["username", "email", "password"])
@pytest.mark.parametrize(
    "bad_value", [MISSING, "", "   "], ids=["missing", "empty", "whitespace"]
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
