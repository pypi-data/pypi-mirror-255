from deprecated import (
    deprecated,
)
from typing import (
    TypeVar,
)

_T = TypeVar("_T")


class _InvalidType(Exception):
    pass


@deprecated("Replaced with generic Exception")  # type: ignore[misc]
class InvalidType(_InvalidType):
    def __init__(self, obj: _InvalidType) -> None:
        super().__init__(obj)


@deprecated("Replaced with generic Exception")  # type: ignore[misc]
def new(caller: str, expected: str, item: _T) -> InvalidType:
    draft = _InvalidType(
        f"{caller} expected `{expected}` not `{str(type(item))}`"
    )
    return InvalidType(draft)
