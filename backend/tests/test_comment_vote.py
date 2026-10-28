import pytest
from flask.testing import FlaskClient
from app import db
from app.models import Comment, CommentVote
from flask import Flask
from typing import Callable, Any

MISSING = object()


def vote(client: FlaskClient, user: dict, comment_id: int, value: int):
    return client.post(
        f"/comments/{str(comment_id)}/vote",
        headers=user["headers"],
        json={"value": value},
    )


def test_comment_vote_like_dislike_cancel(
    app: Flask, client: FlaskClient, comment: dict, make_user: Callable[[str], dict]
):
    user_lst = [make_user(f"user_{i}") for i in range(3)]

    for vote_user, score in zip(user_lst, [1, 2, 3]):
        response = vote(client, vote_user, comment_id=comment["id"], value=1)
        assert response.status_code == 201
        assert response.get_json()["score"] == score

    for vote_user, score in zip(user_lst, [3, 3, 3]):
        response = vote(client, vote_user, comment_id=comment["id"], value=1)
        assert response.status_code == 200
        assert response.get_json()["score"] == score

    for vote_user, score in zip(user_lst, [1, -1, -3]):
        response = vote(client, vote_user, comment_id=comment["id"], value=-1)
        assert response.status_code == 200
        assert response.get_json()["score"] == score

    for vote_user, score in zip(user_lst, [-2, -1, 0]):
        response = vote(client, vote_user, comment_id=comment["id"], value=0)
        assert response.status_code == 200
        assert response.get_json()["score"] == score

        with app.app_context():
            assert (
                db.session.get(
                    CommentVote,
                    {"user_id": vote_user["id"], "comment_id": comment["id"]},
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
def test_comment_vote_with_bad_val(
    app: Flask, client: FlaskClient, user: dict, comment: dict, bad_val: Any
):
    assert vote(client, user, comment["id"], 1).status_code == 201
    with app.app_context():
        score_before = db.session.get(
            CommentVote, {"user_id": user["id"], "comment_id": comment["id"]}
        )
        comment_before = db.session.get(Comment, comment["id"])
    response = vote(client, user, comment["id"], bad_val)

    with app.app_context():
        score_after = db.session.get(
            CommentVote, {"user_id": user["id"], "comment_id": comment["id"]}
        )
        comment_after = db.session.get(Comment, comment["id"])
        assert response.status_code == 400
        assert response.get_json()["error"] == "the value of 'value' is invalid"
        assert score_before is not None and score_after is not None
        assert score_before.value == score_after.value == 1
        assert comment_before is not None and comment_after is not None
        assert comment_before.score == comment_after.score


def test_comment_vote_with_missing_val(
    app: Flask, client: FlaskClient, user: dict, comment: dict
):
    assert vote(client, user, comment["id"], 1).status_code == 201

    with app.app_context():
        score_before = db.session.get(
            CommentVote, {"user_id": user["id"], "comment_id": comment["id"]}
        )
        comment_before = db.session.get(Comment, comment["id"])
    response = client.post(
        f"/comments/{comment['id']}/vote", json={}, headers=user["headers"]
    )

    with app.app_context():
        score_after = db.session.get(
            CommentVote, {"user_id": user["id"], "comment_id": comment["id"]}
        )
        comment_after = db.session.get(Comment, comment["id"])
        assert response.status_code == 400
        assert response.get_json()["error"] == "value of this vote is missing"
        assert score_before is not None and score_after is not None
        assert score_before.value == score_after.value
        assert comment_before is not None and comment_after is not None
        assert comment_before.score == comment_after.score


def test_comment_new_vote_with_0_val(
    app: Flask, client: FlaskClient, user: dict, comment: dict
):

    response = vote(client, user, comment_id=comment["id"], value=0)
    assert response.status_code == 200
    assert response.get_json()["score"] == 0
    with app.app_context():
        assert (
            db.session.get(
                CommentVote, {"user_id": user["id"], "comment_id": comment["id"]}
            )
            is None
        )


def test_vote_with_nonexistent_comment(client: FlaskClient, user: dict):
    response = vote(client, user, 9999, 1)
    assert response.status_code == 404
