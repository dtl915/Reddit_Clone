import pytest
from flask.testing import FlaskClient
from app import db
from app.models import User
from flask import Flask
from typing import Callable


def test_create_post_with_correct_header(
    client: FlaskClient, community: dict, user: dict, post_payload: dict
):
    response = client.post("/posts/", headers=user["headers"], json=post_payload)

    assert response.status_code == 201

    data = response.get_json()
    assert "id" in data
    assert data["community_id"] == community["id"]
    assert data["author_id"] == user["id"]
    assert data["title"] == post_payload["title"]
    assert data["content"] == post_payload["content"]
    assert data["score"] == 0
    assert "created_at" in data
    assert data["community"] == community["name"]
    assert data["author"] == user["username"]


def test_create_post_with_missing_community_id(
    client: FlaskClient, user: dict, post_payload: dict
):
    del post_payload["community_id"]

    response = client.post("/posts/", headers=user["headers"], json=post_payload)

    assert response.status_code == 400
    assert response.get_json()["error"] == "community_id is empty"


def test_create_post_with_invalid_community_id(
    client: FlaskClient, user: dict, post_payload: dict
):
    post_payload["community_id"] = 9999
    response = client.post("/posts/", headers=user["headers"], json=post_payload)

    assert response.status_code == 404


def test_create_post_with_missing_header(
    client: FlaskClient, community: dict, post_payload: dict
):

    response = client.post("/posts/", json=post_payload)

    assert response.status_code == 401
    assert response.get_json()["error"] == "authentication required"


def test_create_post_with_wrong_header(
    client: FlaskClient, community: dict, post_payload: dict
):

    response = client.post(
        "/posts/", json=post_payload, headers={"Authorization": "Bearer wrong_token"}
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "invalid token"


def test_create_post_with_missing_title(
    client: FlaskClient, community: dict, user: dict, post_payload: dict
):
    del post_payload["title"]
    response = client.post("/posts/", headers=user["headers"], json=post_payload)

    assert response.status_code == 400
    assert response.get_json()["error"] == "title is empty"


def test_create_post_with_removed_author(
    app: Flask,
    client: FlaskClient,
    community: dict,
    make_user: Callable[[str], dict],
    post_payload: dict,
):

    ghost = make_user("ghost")

    with app.app_context():
        user_entity = db.session.get(User, ghost["id"])

        db.session.delete(user_entity)
        db.session.commit()

    response = client.post("/posts/", headers=ghost["headers"], json=post_payload)

    assert response.status_code == 401
    assert response.get_json()["error"] == "the account doesn't exist"
