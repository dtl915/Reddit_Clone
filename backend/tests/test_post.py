import pytest
from flask.testing import FlaskClient
from app import db
from app.models import User, Post
from flask import Flask
from typing import Callable, Any

MISSING = object()


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


@pytest.mark.parametrize(
    "bad_val",
    [MISSING, "", "   ", True],
    ids=["does not exist", "empty", "space", "boolean"],
)
def test_create_post_with_missing_community_id(
    client: FlaskClient, user: dict, post_payload: dict, bad_val: Any
):
    if bad_val is MISSING:
        del post_payload["community_id"]
    else:
        post_payload["community_id"] = bad_val

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


@pytest.mark.parametrize(
    "bad_val", [MISSING, "", "  ", 123], ids=["missing", "empty", "space", "wrong type"]
)
def test_create_post_with_bad_title(
    client: FlaskClient, community: dict, user: dict, post_payload: dict, bad_val: Any
):
    if bad_val is MISSING:
        del post_payload["title"]
    else:
        post_payload["title"] = bad_val
    response = client.post("/posts/", headers=user["headers"], json=post_payload)

    assert response.status_code == 400
    assert response.get_json()["error"] == "title is empty"


def test_create_post_with_removed_author(
    app: Flask,
    client: FlaskClient,
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


@pytest.mark.parametrize(
    "bad_val", [MISSING, "", "   "], ids=["missing", "empty", "space"]
)
def test_create_post_with_empty_content(
    app: Flask, client: FlaskClient, user: dict, post_payload: dict, bad_val: Any
):
    if bad_val is MISSING:
        del post_payload["content"]
    else:
        post_payload["content"] = bad_val
    response = client.post("/posts/", headers=user["headers"], json=post_payload)
    assert response.status_code == 201

    with app.app_context():
        post_created = db.session.get(Post, response.get_json()["id"])
        assert post_created is not None
        assert post_created.content is None


@pytest.mark.parametrize("bad_val", [123, {}, True], ids=["int", "dict", "bool"])
def test_create_post_with_bad_content(
    app: Flask, client: FlaskClient, user: dict, post_payload: dict, bad_val: Any
):

    post_payload["content"] = bad_val
    response = client.post("/posts/", headers=user["headers"], json=post_payload)
    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid content"


def test_get_post_with_correct_id(client: FlaskClient, post: dict):
    response = client.get(f"/posts/{post["id"]}")
    assert response.status_code == 200
    assert post == response.get_json()


def test_get_post_with_wrong_id(client: FlaskClient):
    response = client.get(f"/posts/9999")
    assert response.status_code == 404


def test_delete_existing_post(app: Flask, client: FlaskClient, post: dict, user: dict):
    response = client.delete(f"/posts/{post['id']}", headers=user["headers"])
    assert response.status_code == 204

    with app.app_context():
        assert db.session.get(Post, post["id"]) == None


def test_delete_post_with_invalid_id(client: FlaskClient, user: dict):
    response = client.delete(f"/posts/9999", headers=user["headers"])
    assert response.status_code == 404


def test_delete_post_with_missing_header(client: FlaskClient, post: dict, user: dict):
    response = client.delete(f"/posts/{post['id']}")
    assert response.status_code == 401
    assert response.get_json()["error"] == "authentication required"
    get_response = client.get(f"/posts/{post['id']}", headers=user["headers"])
    assert get_response.status_code == 200


def test_delete_post_with_invalid_header(client: FlaskClient, post: dict, user: dict):
    response = client.delete(
        f"/posts/{post['id']}", headers={"Authorization": "Bearer wrong_token"}
    )
    assert response.status_code == 401
    assert response.get_json()["error"] == "invalid token"
    get_response = client.get(f"/posts/{post['id']}", headers=user["headers"])
    assert get_response.status_code == 200


def test_delete_post_with_wrong_user(
    client: FlaskClient, post: dict, make_user: Callable[[str], dict], user: dict
):
    other = make_user("other")
    response = client.delete(f"/posts/{post['id']}", headers=other["headers"])
    assert response.status_code == 403
    assert (
        response.get_json()["error"]
        == "you do not have the permission to delete this post"
    )

    get_response = client.get(f"/posts/{post['id']}", headers=user["headers"])
    assert get_response.status_code == 200
