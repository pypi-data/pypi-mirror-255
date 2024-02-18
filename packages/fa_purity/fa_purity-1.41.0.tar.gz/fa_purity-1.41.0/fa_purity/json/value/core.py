from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from deprecated import (
    deprecated,
)
from fa_purity.frozen import (
    FrozenDict,
    FrozenList,
)
from fa_purity.json.primitive.core import (
    Primitive,
)
from typing import (
    Callable,
    TypeVar,
    Union,
)

UnfoldedJVal = Union[
    FrozenDict[str, "JsonValue"], FrozenList["JsonValue"], Primitive
]
_T = TypeVar("_T")


@deprecated("Replaced. Use `fa_purity.json_2.value.JsonValue` instead")  # type: ignore[misc]
@dataclass(frozen=True)
class JsonValue:
    _value: UnfoldedJVal

    def unfold(
        self,
    ) -> UnfoldedJVal:
        return self._value

    def map(
        self,
        primitive_case: Callable[[Primitive], _T],
        list_case: Callable[[FrozenList[JsonValue]], _T],
        dict_case: Callable[[FrozenDict[str, JsonValue]], _T],
    ) -> _T:
        if isinstance(self._value, tuple):
            return list_case(self._value)
        if isinstance(self._value, FrozenDict):
            return dict_case(self._value)
        return primitive_case(self._value)
