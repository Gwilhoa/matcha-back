import logging
import sys

from config import config
from flask import Flask, Response, request
from flask_apispec import FlaskApiSpec
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from utils.logger import get_console_logger, setup_loggers_color

jwt: JWTManager = JWTManager()
docs: FlaskApiSpec = FlaskApiSpec(document_options=False)
setup_loggers_color()

matcha_logger = get_console_logger("matcha_info")


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    jwt.init_app(app)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    matcha_logger.info(f"Using database {config.DB_NAME}")
    app.logger.info(f"Using environment {config.ENV}")

    from health_check import health_check_blueprint

    app.register_blueprint(health_check_blueprint, url_prefix="")
    docs.init_app(app)

    CORS(app, resources={r"/*": {"origins": "*"}})


    return app
