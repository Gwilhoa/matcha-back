import os
from typing import Final

from dotenv import load_dotenv
from utils.env_getter import EnvironmentGetter


class BaseConfig:
    """Configuration common to all modes (test, dev, prod)"""

    def __init__(self):
        self.env_getter = EnvironmentGetter()

        # JWT
        self.JWT_SECRET_KEY: Final[str] = self.env_getter.get_string(
            "JWT_SECRET", "JWT secret key used for encryption/decryption of JWTs", required=True
        )

        # Database
        self.DB_USER: Final[str] = self.env_getter.get_string("DB_USER", "Name of the database user", required=True)
        self.DB_PASS: Final[str] = self.env_getter.get_string("DB_PASS", "Password of the database user", required=True)
        self.DB_NAME: Final[str] = self.env_getter.get_string("DB_NAME", "Name of the database", required=True)
        self.DB_IP: Final[str] = self.env_getter.get_string("DB_IP", "Adress of the database", required=True)
        self.DB_PORT: Final[str] = self.env_getter.get_string("DB_PORT", "Port of the database", required=True)
        self.SQLALCHEMY_DATABASE_URI: Final[str] = f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_IP}:{self.DB_PORT}/{self.DB_NAME}"

        self.DEBUG: bool = self.env_getter.get_bool("DEBUG", required=False)


class TestingConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.ENV = "test"

        self.env_getter.fail_if_missing()


class DevelopmentConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.ENV = "dev"

        self.env_getter.fail_if_missing()


class ProductionConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.ENV = "prod"

        self.env_getter.fail_if_missing()


load_dotenv()
match os.getenv("ENV"):
    case "test":
        config = TestingConfig()
    case "prod":
        config = ProductionConfig()
    case "dev" | None:
        config = DevelopmentConfig()
    case _:
        raise Exception("Missing environment variable named ENV (possible values): test | prod | dev (default: dev)")
