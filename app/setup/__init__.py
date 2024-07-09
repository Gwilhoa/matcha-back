import logging
import sys

from config import config
from flask import Flask, Response, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from managers.database_manager.database_connection import DatabaseConnection, ModelInterface
from utils.logger import get_console_logger, setup_loggers_color
from flask_openapi3 import OpenAPI, Info

jwt: JWTManager = JWTManager()
setup_loggers_color()

matcha_logger = get_console_logger("matcha_info")
db = DatabaseConnection(config)

class testModel(ModelInterface):
    id_test = db.STRING(nullable=False, primary_key=True)
    name = db.STRING(nullable=True)


def create_app():
    info = Info(title="Matcha API", version="0.0.0b")
    app = OpenAPI(__name__, info=info, doc_prefix="/docs")
    app.config.from_object(config)

    jwt.init_app(app)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    matcha_logger.info(f"Using database {config.DB_NAME}")
    app.logger.info(f"Using environment {config.ENV}")

    from health_check import health_check_blueprint

    app.register_api(health_check_blueprint)

    CORS(app, resources={r"/*": {"origins": "*"}})

    db.create_table()
    return app
