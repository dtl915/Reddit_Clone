import os
import secrets
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

load_dotenv()


def parse_origins(origins: str | None) -> list[str]:
    if origins is None:
        return []
    else:
        origins_lst = []
        for origin in origins.split(","):
            if origin.strip():
                origins_lst.append(origin.strip(", "))
        return origins_lst


class ConfigError(RuntimeError):
    """Required configuration is missing or unsafe."""


class Config:
    DATABASE_ENV_VAR = "DATABASE_URL"
    SQLALCHEMY_DATABASE_URI = os.environ.get(DATABASE_ENV_VAR)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    BCRYPT_ROUNDS = 12
    CORS_ORIGINS = parse_origins(os.environ.get("CORS_ORIGINS"))

    @classmethod
    def check_env(cls) -> None:
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ConfigError(f"{cls.DATABASE_ENV_VAR} is not set")
        if not cls.JWT_SECRET_KEY:
            raise ConfigError("JWT_SECRET_KEY is not set")
        if len(cls.JWT_SECRET_KEY) < 64:
            raise ConfigError(
                "JWT_SECRET_KEY is too short (need at least 64 characters; generate one with: python -c 'import secrets; print(secrets.token_hex(32))')"
            )


class TestingConfig(Config):
    TESTING = True
    DATABASE_ENV_VAR = "TEST_DATABASE_URL"
    SQLALCHEMY_DATABASE_URI = os.environ.get(DATABASE_ENV_VAR)
    JWT_SECRET_KEY = secrets.token_hex(32)
    BCRYPT_ROUNDS = 4

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

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 3,
        "max_overflow": 2,
        "pool_pre_ping": True,
        "pool_recycle": 300,  # seconds
    }

    @classmethod
    def check_env(cls) -> None:
        super().check_env()
        if not cls.CORS_ORIGINS:
            raise ConfigError("CORS_ORIGINS is not set")
        for origin in cls.CORS_ORIGINS:
            url = urllib.parse.urlsplit(origin)

            if (
                url.scheme != "https"
                or not url.netloc
                or url.path
                or url.query
                or url.fragment
            ):
                raise ConfigError(
                    f"Illegal origin in CORS_ORIGINS: {origin} (expected https://host[:port])"
                )


class DevelopmentConfig(Config):
    DEBUG = True
    CORS_ORIGINS = parse_origins(os.environ.get("CORS_ORIGINS")) or [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


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
            f"Unknown APP_ENV {name!r}; expected one of: {", ".join(CONFIGS)}"
        )
