import os
from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

load_dotenv()


class ConfigError(RuntimeError):
    """Required configuration is missing or unsafe."""


class Config:
    DATABASE_ENV_VAR = "DATABASE_URL"
    SQLALCHEMY_DATABASE_URI = os.environ.get(DATABASE_ENV_VAR)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

    @classmethod
    def check_env(cls) -> None:
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ConfigError(f"{cls.DATABASE_ENV_VAR} is not set")
        if not cls.JWT_SECRET_KEY:
            raise ConfigError("JWT_SECRET_KEY is not set")


class TestingConfig(Config):
    TESTING = True
    DATABASE_ENV_VAR = "TEST_DATABASE_URL"
    SQLALCHEMY_DATABASE_URI = os.environ.get(DATABASE_ENV_VAR)
    JWT_SECRET_KEY = "jwt-secret-key-for-tests"

    @classmethod
    def check_env(cls) -> None:
        super().check_env()
        assert cls.SQLALCHEMY_DATABASE_URI is not None
        try:
            url = make_url(cls.SQLALCHEMY_DATABASE_URI)
        except ArgumentError:
            raise ConfigError(
                f"{cls.DATABASE_ENV_VAR} is not a valid database URL"
            ) from None

        if url.database is None or not url.database.endswith("_test"):
            raise ConfigError(
                f"Refusing to run tests against database '{url.database}': name must end with '_test'"
            )


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


CONFIGS: dict[str, type[Config]] = {
    "testing": TestingConfig,
    "production": ProductionConfig,
    "development": DevelopmentConfig,
}

DEFAULT_ENV = "development"


def get_config(name: str | None = None) -> type[Config]:
    if not name:
        name = DEFAULT_ENV

    if name in CONFIGS:
        return CONFIGS[name]
    else:
        raise ConfigError(
            f"Unknown APP_ENV {name!r}; expected one of: {", ".join([key for key in CONFIGS])}"
        )
