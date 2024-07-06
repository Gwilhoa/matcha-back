import os

from .errors import SeveralEnvironmentVariablesNotFound, WrongBooleanValueError
from .types import EnvironmentVariableSpec


class EnvironmentGetter:
    def __init__(self):
        self.variables: list[EnvironmentVariableSpec] = []

    def get_string(self, variable_name, description=None, *, required=True, validate=None):
        value = os.getenv(variable_name)
        self.variables.append(
            {
                "name": variable_name,
                "description": description,
                "value": value,
                "required": required,
                "validate": validate,
            }
        )
        return value

    def get_bool(self, variable_name, description=None, *, required=True):
        value = self.get_string(variable_name, description=description, required=required)

        truish = ["1", "true", "t", "y", "yes"]
        falsish = ["0", "false", "f", "n", "no"]
        if value is None:
            return None
        elif value.lower() in truish:
            return True
        elif value.lower() in falsish:
            return False
        else:
            raise WrongBooleanValueError(variable_name, value)

    def fail_if_missing(self):
        error_variables = [variable for i, variable in enumerate(self.variables) if variable["required"] and (variable["value"] is None)]
        if len(error_variables) == 0:
            return

        raise SeveralEnvironmentVariablesNotFound(error_variables)
