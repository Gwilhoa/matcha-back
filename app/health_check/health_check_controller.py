from flask_openapi3 import APIBlueprint, Tag

from setup import db

NAME = "health_check"
health_check_blueprint = APIBlueprint(f"{NAME}_blueprint", url_prefix="", import_name=__name__)
TAG = Tag(name="Health Check", description="Check if the database is connected")


@health_check_blueprint.get("/", tags=[TAG], description="Check if the database is connected",
                            responses={200: {"msg": "Database is connected"},
                                       400: {"msg": "Database is not connected"}})
def do_health_check():
    """
    Check if the database is connected
    """
    if not db.health_check():
        return {"msg": "Database is not connected"}, 400
    return {"msg": "Database is connected"}, 200
