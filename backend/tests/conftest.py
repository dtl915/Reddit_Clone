import pytest
from flask import Flask
from collections.abc import Iterator
from app import create_app, db
from config import TestingConfig


@pytest.fixture(scope="session")
def app() -> Iterator[Flask]:
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
