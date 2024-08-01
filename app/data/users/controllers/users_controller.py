from flask import Blueprint, request
from managers.swagger_manager import swagger
from setup import docs
from utils.logger import get_console_logger

from data.users.models import UserModel

NAME = 'users'

users_blueprint = Blueprint(f'{NAME}_blueprint', __name__)
user_logger = get_console_logger(__name__)


@swagger(
    responses={
        200: {'description': 'User created successfully', 'content': UserModel},
    },
    body={'description': 'The user to create', 'content': UserModel},
)
@users_blueprint.post(f'{NAME}/')
def create_user():
    data = request.get_json()
    user = UserModel.load(data)
    user_logger.debug(user.dump())
    return_user: UserModel = user.create_one()
    return return_user.dump(), 200


docs.register_function(create_user, users_blueprint)
