import pytest
from flask.testing import FlaskClient
from app import db
from app.models import Post, PostVote
from flask import Flask
from typing import Callable, Any

MISSING = object()


def vote(client: FlaskClient, user: dict, post_id: int, value: int):
    return client.post(
        f"/posts/{str(post_id)}/vote", headers=user["headers"], json={"value": value}
    )


def test_post_vote_like_dislike_cancel(
    app: Flask, client: FlaskClient, post: dict, make_user: Callable[[str], dict]
):
    user_lst = [make_user(f"user_{i}") for i in range(3)]

    for vote_user, score in zip(user_lst, [1, 2, 3]):
        response = vote(client, vote_user, post_id=post["id"], value=1)
        assert response.status_code == 201
        assert response.get_json()["score"] == score

    for vote_user, score in zip(user_lst, [3, 3, 3]):
        response = vote(client, vote_user, post_id=post["id"], value=1)
        assert response.status_code == 200
        assert response.get_json()["score"] == score

    for vote_user, score in zip(user_lst, [1, -1, -3]):
        response = vote(client, vote_user, post_id=post["id"], value=-1)
        assert response.status_code == 200
        assert response.get_json()["score"] == score

    for vote_user, score in zip(user_lst, [-2, -1, 0]):
        response = vote(client, vote_user, post_id=post["id"], value=0)
        assert response.status_code == 200
        assert response.get_json()["score"] == score

        with app.app_context():
            assert (
                db.session.get(
                    PostVote, {"user_id": vote_user["id"], "post_id": post["id"]}
                )
                is None
            )


@pytest.mark.parametrize(
    "bad_val",
    [1.0, "1", 100, True, 2, -2, 1.1, "abc", None, []],
    ids=[
        "float",
        "str",
        "large int",
        "bool",
        "upper-edge",
        "lower-edge",
        "1.1",
        "abc",
        "None",
        "list",
    ],
)
def test_post_vote_with_bad_val(
    app: Flask, client: FlaskClient, user: dict, post: dict, bad_val: Any
):
    assert vote(client, user, post["id"], 1).status_code == 201
    with app.app_context():
        score_before = db.session.get(
            PostVote, {"user_id": user["id"], "post_id": post["id"]}
        )
        post_before = db.session.get(Post, post["id"])
    response = vote(client, user, post["id"], bad_val)

    with app.app_context():
        score_after = db.session.get(
            PostVote, {"user_id": user["id"], "post_id": post["id"]}
        )
        post_after = db.session.get(Post, post["id"])
        assert response.status_code == 400
        assert "error" in response.get_json()
        assert score_before is not None and score_after is not None
        assert score_before.value == score_after.value
        assert post_before is not None and post_after is not None
        assert post_before.score == post_after.score


def test_post_vote_with_missing_val(
    app: Flask, client: FlaskClient, user: dict, post: dict
):
    assert vote(client, user, post["id"], 1).status_code == 201

    with app.app_context():
        score_before = db.session.get(
            PostVote, {"user_id": user["id"], "post_id": post["id"]}
        )
        post_before = db.session.get(Post, post["id"])
    response = client.post(
        f"/posts/{post['id']}/vote", json={}, headers=user["headers"]
    )

    with app.app_context():
        score_after = db.session.get(
            PostVote, {"user_id": user["id"], "post_id": post["id"]}
        )
        post_after = db.session.get(Post, post["id"])
        assert response.status_code == 400
        assert response.get_json()["error"] == "value of this vote is missing"
        assert score_before is not None and score_after is not None
        assert score_before.value == score_after.value
        assert post_before is not None and post_after is not None
        assert post_before.score == post_after.score


def test_post_new_vote_with_0_val(
    app: Flask, client: FlaskClient, user: dict, post: dict
):

    response = vote(client, user, post_id=post["id"], value=0)
    assert response.status_code == 200
    assert response.get_json()["score"] == 0
    with app.app_context():
        assert (
            db.session.get(PostVote, {"user_id": user["id"], "post_id": post["id"]})
            is None
        )


def test_vote_with_no_token(client: FlaskClient, post: dict):
    response = vote(client, {"headers": {}}, post["id"], 1)
    assert response.status_code == 401


def test_vote_with_nonexistent_post(client: FlaskClient, user: dict):
    response = vote(client, user, 9999, 1)
    assert response.status_code == 404
