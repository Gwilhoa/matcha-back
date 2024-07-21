from flask import Blueprint
from managers.swagger_manager.doc_decorator import swagger
from marshmallow import fields
from setup import TestModel, db, docs

NAME = 'health_check'
health_check_blueprint = Blueprint(f'{NAME}_blueprint', url_prefix='', import_name=__name__)


@swagger(
    responses={
        200: {'description': 'Backend is up and database connection is successful', 'content': {'message': fields.String()}},
        500: {'description': 'Backend is up but database connection failed', 'content': TestModel},
    },
)
@health_check_blueprint.get('/')
def do_health_check():
    if not db.health_check():
        return {'msg': 'Database is not connected'}, 400
    return {'msg': 'Database is connected'}, 200


docs.register_function(do_health_check, health_check_blueprint)
