from .types import EnvironmentVariableSpec


class SeveralEnvironmentVariablesNotFoundError(Exception):
    def __init__(self, error_variables: list[EnvironmentVariableSpec]):
        message = 'One or several environment variables are missing.\n'
        message += '\n'.join(SeveralEnvironmentVariablesNotFoundError._format_one_error(variable) for variable in error_variables)

        super().__init__(message)

    @staticmethod
    def _format_one_error(variable: EnvironmentVariableSpec) -> str:
        message_one = '- ' + variable['name']
        if variable['description'] is not None:
            message_one += f": {variable['description']}"
        return message_one


class WrongBooleanValueError(Exception):
    def __init__(self, variable_name: str, value: str):
        message = f'Wrong value for the boolean variable {variable_name}: {value}'
        super().__init__(message)
