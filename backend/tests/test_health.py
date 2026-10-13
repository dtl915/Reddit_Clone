import pytest
from flask.testing import FlaskClient


def test_health(client: FlaskClient):
    response = client.get("/health")
    assert response.status_code == 200 and response.get_json()["status"] == "ok"
