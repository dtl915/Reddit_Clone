from typing import Any, Callable
import pytest
from flask import Flask
from flask.testing import FlaskClient
from app.models import Comment

MISSING = object()


def test_create_comment_and_parent(
    app: Flask, client: FlaskClient, user: dict, post: dict
):
    response1 = client.post(
        "/comments/",
        headers=user["headers"],
        json={"parent_id": None, "post_id": post["id"], "content": "test-comment"},
    )

    data1 = response1.get_json()
    assert response1.status_code == 201

    response2 = client.post(
        "/comments/",
        headers=user["headers"],
        json={
            "parent_id": data1["id"],
            "post_id": post["id"],
            "content": "test-comment-2",
        },
    )

    assert response2.status_code == 201
    data2 = response2.get_json()

    with app.app_context():
        comment1 = Comment.query.get(data1["id"])
        comment2 = Comment.query.get(data2["id"])
        assert comment1 is not None and comment2 is not None
        assert comment1.parent_id is None
        assert comment2.parent_id == comment1.id
        assert comment1.post_id == post["id"]
        assert comment2.post_id == post["id"]
        assert comment1.content == "test-comment"
        assert comment2.content == "test-comment-2"


@pytest.mark.parametrize("fields", ["post_id", "content"])
@pytest.mark.parametrize(
    "value",
    [MISSING, None, "", "  ", True, [], {}],
    ids=["missing", "none", "empty", "whitespace", "bool", "list", "dict"],
)
def test_create_comment_with_bad_val(
    client: FlaskClient,
    user: dict,
    comment_payload: dict,
    fields: str,
    value: Any,
):
    payload = comment_payload.copy()

    if value is MISSING:
        del payload[fields]
    else:
        payload[fields] = value

    response = client.post("/comments/", headers=user["headers"], json=payload)
    assert response.status_code == 400
    assert response.get_json() == {"error": f"{fields} cannot be empty"}


def test_create_comment_with_nonexisting_post(
    client: FlaskClient, user: dict, comment_payload: dict
):
    comment_payload["post_id"] = 9999
    response = client.post("/comments/", headers=user["headers"], json=comment_payload)
    assert response.status_code == 404
    assert response.get_json() == {"error": "not found"}


def test_create_comment_with_missing_header(client: FlaskClient, comment_payload: dict):
    response = client.post("/comments/", json=comment_payload)
    assert response.status_code == 401
    assert response.get_json() == {"error": "authentication required"}


def test_create_comment_with_nonexisting_parent(
    client: FlaskClient, user: dict, comment_payload: dict
):
    comment_payload["parent_id"] = 9999
    response = client.post("/comments/", headers=user["headers"], json=comment_payload)
    assert response.status_code == 404
    assert response.get_json() == {"error": "not found"}


def test_create_comment_with_invalid_parent(
    client: FlaskClient,
    user: dict,
    community: dict,
    make_post: Callable[[int, dict], dict],
    make_comment: Callable[[int, int | None, dict], dict],
):
    post1 = make_post(community["id"], user["headers"])
    post2 = make_post(community["id"], user["headers"])

    comment1 = make_comment(post1["id"], None, user["headers"])

    comment2_response = client.post(
        "/comments/",
        headers=user["headers"],
        json={
            "post_id": post2["id"],
            "parent_id": comment1["id"],
            "content": "test-content-2",
        },
    )

    assert comment2_response.status_code == 400
    assert comment2_response.get_json()["error"] == "invalid parent_id or post_id"


def test_get_comment(client: FlaskClient, comment: dict):
    response = client.get(f"/comments/{comment['id']}")
    data = response.get_json()
    assert response.status_code == 200
    assert data["id"] == comment["id"]


def test_get_nonexisting_comment(client: FlaskClient):
    response = client.get("/comments/9999")
    assert response.status_code == 404


def test_delete_comment(client: FlaskClient, user: dict, comment: dict):
    response = client.delete(f"/comments/{comment['id']}", headers=user["headers"])
    assert response.status_code == 204


def test_delete_comment_with_nonexisting_comment(client: FlaskClient, user: dict):
    response = client.delete("/comments/9999", headers=user["headers"])
    assert response.status_code == 404


def test_delete_comment_with_wrong_header(
    client: FlaskClient, comment: dict, make_user: Callable[[str], dict]
):
    other = make_user("other")
    response = client.delete(f"/comments/{comment['id']}", headers=other["headers"])
    assert response.status_code == 403
    assert (
        response.get_json()["error"]
        == "you do not have the permission to delete this comment"
    )
