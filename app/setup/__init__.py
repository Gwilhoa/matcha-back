import logging
import sys

from config import config
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from managers.database_manager.database_connection import DatabaseConnection, ModelInterface
from managers.swagger_manager import SwaggerInterface
from managers.swagger_manager.swagger_interface import SwaggerParams
from utils.logger import get_console_logger, setup_loggers_color

jwt: JWTManager = JWTManager()
setup_loggers_color()

matcha_logger = get_console_logger('matcha_info')
db = DatabaseConnection(config)

PARAMS = SwaggerParams(
    title='Quick Start API',
    version='0.0.0',
    openapi_version='3.0.2',
    components={'securitySchemes': {'ApiKeyAuth': {'type': 'apiKey', 'in': 'header', 'name': 'Authorization'}}},
    security_definitions={'ApiKeyAuth': {'type': 'apiKey', 'name': 'Authorization', 'in': 'header'}},
    security=[{'ApiKeyAuth': []}],
    info={
        'description': 'how to use the API with the authorization: \n'
        '1.	Enter your credentials: Provide your username and password in the authentication route below. \n'
        '2.	Retrieve the key: Upon successful authentication, you will receive an authentication key. \n'
        '3.	Authorize: Add the returned key by clicking on the “Authorize” button.'
    },
)
docs: SwaggerInterface = SwaggerInterface(PARAMS)


class TestModel(ModelInterface):
    id_test = db.string(nullable=False, primary_key=True)
    name = db.string(nullable=True)


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    jwt.init_app(app)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    matcha_logger.info(f'Using database {config.DB_NAME}')
    app.logger.info(f'Using environment {config.ENV}')

    from health_check import health_check_blueprint

    app.register_blueprint(health_check_blueprint)

    docs.init_app(app)

    CORS(app, resources={r'/*': {'origins': '*'}})

    db.create_table()

    test = TestModel()
    test.id_test = '1'
    test.name = 'test'
    test.create_one()
    return app
