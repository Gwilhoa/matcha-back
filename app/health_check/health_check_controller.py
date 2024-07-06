from flask import Blueprint

NAME = "health_check"
health_check_blueprint = Blueprint(f"{NAME}_blueprint", __name__)


@health_check_blueprint.get("/")
def do_health_check():
    return {"msg": "Database is connected"}, 200
