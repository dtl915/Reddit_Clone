import pytest
import itertools
from flask import Flask
from flask.testing import FlaskClient
from collections.abc import Iterator
from app import create_app, db
from config import TestingConfig
from sqlalchemy import text
from typing import Callable


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
        "id": data["id"],
    }

    return info


@pytest.fixture(scope="function")
def auth_headers(client: FlaskClient, registered_user: dict[str, str]):
    response = client.post("/auth/login", json=registered_user)
    assert response.status_code == 200

    data = response.get_json()

    return {"Authorization": f"Bearer {data["access_token"]}"}


@pytest.fixture
def make_user(client: FlaskClient) -> Callable[[str], dict]:
    counter = itertools.count()

    def _make_user(username: str):
        info = {
            "username": username,
            "email": f"user{next(counter)}@example.com",
            "password": "test-password",
        }
        register_response = client.post(
            "/auth/register",
            json=info,
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/auth/login", json={"email": info["email"], "password": info["password"]}
        )
        assert login_response.status_code == 200
        token = login_response.get_json()["access_token"]

        return {
            "id": register_response.get_json()["id"],
            "headers": {"Authorization": f"Bearer {token}"},
            **info,
        }

    return _make_user


@pytest.fixture
def user(make_user: Callable[[str], dict]) -> dict:
    return make_user("author")


@pytest.fixture
def community(client: FlaskClient, user: dict):

    payload = {
        "name": "test-community",
        "description": "this is a test community",
    }

    response = client.post("/communities/", json=payload, headers=user["headers"])
    assert response.status_code == 201

    return response.get_json()


@pytest.fixture
def post_payload(community: dict):
    return {
        "community_id": community["id"],
        "title": "test-post",
        "content": "test-content",
    }
