import pytest
from flask.testing import FlaskClient
from flask import Flask
from app import db
from app.models import Community


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


def test_create_community_with_missing_name(
    app: Flask, client: FlaskClient, user: dict, community_payload: dict
):
    del community_payload["name"]
    response = client.post(
        "/communities/", headers=user["headers"], json=community_payload
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "name cannot be empty"
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
