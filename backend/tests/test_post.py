import pytest
from flask.testing import FlaskClient
from app import db
from app.models import User
from flask import Flask
from typing import Callable


def test_create_post_with_correct_header(
    client: FlaskClient, community: dict, user: dict
):
    payload = {
        "community_id": community["id"],
        "title": "test-post",
        "content": "test-content",
    }
    response = client.post("/posts/", headers=user["headers"], json=payload)

    assert response.status_code == 200

    data = response.get_json()
    assert "id" in data
    assert data["community_id"] == community["id"]
    assert data["author_id"] == user["id"]
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["score"] == 0
    assert "created_at" in data
    assert data["community"] == community["name"]
    assert data["author"] == user["username"]


def test_create_post_with_missing_community_id(client: FlaskClient, user: dict):
    payload = {
        "title": "test-post",
        "content": "test-content",
    }
    response = client.post("/posts/", headers=user["headers"], json=payload)

    assert response.status_code == 400
    assert response.get_json()["error"] == "community_id is empty"


def test_create_post_with_invalid_community_id(client: FlaskClient, user: dict):
    payload = {
        "community_id": 9999,
        "title": "test-post",
        "content": "test-content",
    }
    response = client.post("/posts/", headers=user["headers"], json=payload)

    assert response.status_code == 401
    assert response.get_json()["error"] == "the community doesn't exist"


def test_create_post_with_missing_header(client: FlaskClient, community: dict):
    payload = {
        "community_id": community["id"],
        "title": "test-post",
        "content": "test-content",
    }
    response = client.post("/posts/", json=payload)

    assert response.status_code == 401
    assert response.get_json()["error"] == "authentication required"


def test_create_post_with_wrong_header(client: FlaskClient, community: dict):
    payload = {
        "community_id": community["id"],
        "title": "test-post",
        "content": "test-content",
    }
    response = client.post(
        "/posts/", json=payload, headers={"Authorization": "Bearer wrong_token"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "invalid token"


def test_create_post_with_missing_title(
    client: FlaskClient, community: dict, user: dict
):
    payload = {
        "community_id": community["id"],
        "content": "test-content",
    }
    response = client.post("/posts/", headers=user["headers"], json=payload)

    assert response.status_code == 400
    assert response.get_json()["error"] == "title is empty"


def test_create_post_with_removed_author(
    app: Flask, client: FlaskClient, community: dict, make_user: Callable[[str], dict]
):

    user = make_user("ghost")

    with app.app_context():
        user_entity = db.session.get(User, user["id"])

        db.session.delete(user_entity)
        db.session.commit()

    payload = {
        "community_id": community["id"],
        "title": "test-post",
        "content": "test-content",
    }

    response = client.post("/posts/", headers=user["headers"], json=payload)

    assert response.status_code == 401
    assert response.get_json()["error"] == "the account doesn’t exist"
