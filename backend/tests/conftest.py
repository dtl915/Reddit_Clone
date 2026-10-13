import pytest
from flask import Flask
from collections.abc import Iterator
from app import create_app, db
from config import TestingConfig
from sqlalchemy import text


@pytest.fixture(scope="session")
def app() -> Iterator[Flask]:
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(autouse=True)
def clean_db(app):
    yield
    with app.app_context():
        db.session.remove()
        db.session.execute(
            text(
                f"TRUNCATE TABLE {", ".join([f'"{table.name}"' for table in db.metadata.sorted_tables])} RESTART IDENTITY CASCADE"
            )
        )

        db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()
