import pytest
from flask.testing import FlaskClient
from flask import Flask
from app import db
from app.models import Community, Post
from typing import Callable

MISSING = object()


def test_create_community_success(
    app: Flask, client: FlaskClient, user: dict, community_payload: dict
):

    response = client.post(
        "/communities/", headers=user["headers"], json=community_payload
    )
    assert response.status_code == 201
    data = response.get_json()
    with app.app_context():
        community = db.session.get(Community, data["id"])
        assert community is not None
        assert community.name == community_payload["name"]
        assert community.creator_id == user["id"]
        assert community.description == community_payload["description"]


@pytest.mark.parametrize("name", ["", "  ", MISSING])
def test_create_community_with_bad_name(
    app: Flask, client: FlaskClient, user: dict, community_payload: dict, name: str
):
    if name is MISSING:
        del community_payload["name"]
    else:
        community_payload["name"] = name
    response = client.post(
        "/communities/", headers=user["headers"], json=community_payload
    )
    assert response.status_code == 400
    assert "error" in response.get_json()
    with app.app_context():
        community = db.session.query(Community).all()
        assert len(community) == 0


def test_create_community_with_existing_name(
    app: Flask,
    client: FlaskClient,
    user: dict,
    community_payload: dict,
):
    response1 = client.post(
        "/communities/", headers=user["headers"], json=community_payload
    )
    assert response1.status_code == 201
    response2 = client.post(
        "/communities/", headers=user["headers"], json=community_payload
    )

    assert response2.status_code == 409
    assert response2.get_json()["error"] == "the name of this community already taken"
    with app.app_context():
        community_lst = db.session.query(Community).all()
        assert len(community_lst) == 1


@pytest.mark.parametrize("field", ["name", "description"])
@pytest.mark.parametrize(
    "val", [123, 1.0, True, [], {}], ids=["123", "1.0", "True", "list", "set"]
)
def test_create_community_with_bad_val(
    app: Flask,
    client: FlaskClient,
    user: dict,
    community_payload: dict,
    field: str,
    val: str,
):
    community_payload[field] = val
    response = client.post(
        "/communities/", headers=user["headers"], json=community_payload
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == f"{field} is invalid"

    with app.app_context():
        community_lst = db.session.query(Community).all()
        assert len(community_lst) == 0


@pytest.mark.parametrize("val", [None, "", "  "])
def test_create_community_with_missing_description(
    app: Flask,
    client: FlaskClient,
    user: dict,
    community_payload: dict,
    val: str,
):
    community_payload["description"] = val
    response = client.post(
        "/communities/", headers=user["headers"], json=community_payload
    )
    assert response.status_code == 201
    data = response.get_json()
    with app.app_context():
        community = db.session.get(Community, data["id"])
        assert community is not None
        assert community.name == community_payload["name"]
        assert community.creator_id == user["id"]
        assert community.description == community_payload["description"]


def test_get_and_list_community(client: FlaskClient, community: dict):
    response_list_cm = client.get("/communities/")
    response_get_cm = client.get(f"/communities/{community["id"]}")

    assert response_get_cm.status_code == response_list_cm.status_code == 200
    assert response_get_cm.get_json() == response_list_cm.get_json()[0]
    assert response_get_cm.get_json() == community
    assert response_list_cm.get_json() == [community]


@pytest.mark.parametrize("action", ["GET", "DELETE"])
def test_actions_on_nonexisting_community(
    client: FlaskClient, user: dict, community_payload: dict, action: str
):
    response = None

    if action == "GET":
        response = client.get("/communities/9999", headers=user["headers"])
    elif action == "DELETE":
        response = client.delete("/communities/9999", headers=user["headers"])

    assert response is not None
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_delete_community(
    app: Flask,
    client: FlaskClient,
    user: dict,
    community: dict,
    make_post: Callable[[int, dict], dict],
):
    post = make_post(community["id"], user["headers"])
    response = client.delete(f"/communities/{community["id"]}", headers=user["headers"])
    assert response.status_code == 204

    with app.app_context():
        deleted_community = db.session.get(Community, community["id"])
        assert deleted_community is None

        deleted_post = db.session.get(Post, post["id"])
        assert deleted_post is None


def test_delete_community_with_wrong_user(
    app: Flask, client: FlaskClient, community: dict, make_user: Callable[[str], dict]
):
    other = make_user("other")
    response = client.delete(
        f"/communities/{community["id"]}", headers=other["headers"]
    )

    data = response.get_json()["error"]

    assert response.status_code == 403
    assert data == "you do not have the permission to delete this community"

    with app.app_context():
        community_to_be_delete = db.session.get(Community, community["id"])
        assert community_to_be_delete is not None


def test_actions_on_missing_header(
    client: FlaskClient, community_payload: dict, user: dict
):
    response_create_fail = client.post(
        "/communities/", headers={}, json=community_payload
    )
    assert response_create_fail.status_code == 401

    response_create_success = client.post(
        "/communities/", headers=user["headers"], json=community_payload
    )
    assert response_create_success.status_code == 201

    response_delete_fail = client.delete(
        f"/communities/{response_create_success.get_json()["id"]}", headers={}
    )
    assert response_delete_fail.status_code == 401
