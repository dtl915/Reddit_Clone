import pytest
from pytest import MonkeyPatch
from flask.testing import FlaskClient
from flask import Flask


def test_error_handler_500(app: Flask, monkeypatch: MonkeyPatch, client: FlaskClient):

    def error_500(*args, **kwargs):
        raise RuntimeError("secret detail")

    monkeypatch.setitem(app.config, "PROPAGATE_EXCEPTIONS", False)
    monkeypatch.setitem(app.view_functions, "posts.get_recent_posts", error_500)

    response = client.get("/posts/")
    assert response.status_code == 500
    assert response.is_json
    assert "error" in response.get_json()
    assert "secret detail" not in response.get_data(as_text=True)


def test_error_handler_404(client: FlaskClient):

    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.is_json
    assert "error" in response.get_json()


def test_error_handler_405_wrong_method(client: FlaskClient):
    response = client.post("/health")
    assert response.status_code == 405
    assert response.is_json
    assert "error" in response.get_json()
