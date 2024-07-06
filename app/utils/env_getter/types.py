from collections.abc import Callable
from typing import TypedDict


class EnvironmentVariableSpec(TypedDict):
    name: str
    description: str | None
    value: str | None
    required: bool
    validate: Callable[[str], bool] | None
