from deprecated import (
    deprecated,
)
from fa_purity._core.coproduct import (
    Coproduct,
    CoproductFactory,
    CoproductTransform,
    UnionFactory,
)
from typing import (
    Optional,
    Type,
    TypeVar,
    Union,
)

_L = TypeVar("_L")
_R = TypeVar("_R")


@deprecated("NEW API: use `UnionFactory` instead")  # type: ignore[misc]
def inr(val: _R, _left: Optional[Type[_L]] = None) -> Union[_L, _R]:
    return val


@deprecated("NEW API: use `UnionFactory` instead")  # type: ignore[misc]
def inl(val: _L, _right: Optional[Type[_R]] = None) -> Union[_L, _R]:
    return val


__all__ = [
    "Coproduct",
    "CoproductFactory",
    "CoproductTransform",
    "UnionFactory",
]
