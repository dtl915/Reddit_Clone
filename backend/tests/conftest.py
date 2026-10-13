import pytest
from flask import Flask
from flask.testing import FlaskClient
from collections.abc import Iterator
from app import create_app, db
from config import TestingConfig
from sqlalchemy import text


@pytest.fixture(scope="session")
def app() -> Iterator[Flask]:
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    yield
    with app.app_context():
        db.session.remove()
        db.session.execute(
            text(
                f"TRUNCATE TABLE {", ".join([f'"{table.name}"' for table in db.metadata.sorted_tables])} RESTART IDENTITY CASCADE"
            )
        )

        db.session.commit()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(scope="function")
def registered_user(client: FlaskClient):
    username = "test"
    email = "test@example.com"
    password = "test-password"
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )

    assert response.status_code == 201

    data = response.get_json()

    info = {
        "username": data["username"],
        "email": data["email"],
        "password": password,
        "ID": data["ID"],
    }

    return info


@pytest.fixture(scope="function")
def auth_headers(client: FlaskClient, registered_user: dict[str, str]):
    response = client.post("/auth/login", json=registered_user)
    assert response.status_code == 200

    data = response.get_json()

    return {"Authorization": f"Bearer {data["access_token"]}"}
