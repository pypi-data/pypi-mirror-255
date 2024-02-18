from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
    field,
)
from fa_purity.frozen import (
    FrozenDict,
    FrozenList,
)
from fa_purity.json.primitive.core import (
    Primitive,
)
from fa_purity.union import (
    Coproduct,
)
from typing import (
    Callable,
    TypeVar,
    Union,
)

UnfoldedJVal = Union[
    FrozenDict[str, "JsonValue"], FrozenList["JsonValue"], Primitive
]
from fa_purity.json_2.primitive import (
    JsonPrimitive,
)

_T = TypeVar("_T")


@dataclass(frozen=True)
class _Private:
    pass


JsonObj = FrozenDict[str, "JsonValue"]


@dataclass(frozen=True)
class JsonValue:
    "The type for json values"
    _private: _Private = field(repr=False, hash=False, compare=False)
    _value: Coproduct[JsonPrimitive, Coproduct[JsonObj, FrozenList[JsonValue]]]

    def map(
        self,
        primitive_case: Callable[[JsonPrimitive], _T],
        list_case: Callable[[FrozenList[JsonValue]], _T],
        dict_case: Callable[[FrozenDict[str, JsonValue]], _T],
    ) -> _T:
        return self._value.map(
            primitive_case, lambda c: c.map(dict_case, list_case)
        )

    @staticmethod
    def from_primitive(item: JsonPrimitive) -> JsonValue:
        return JsonValue(_Private(), Coproduct.inl(item))

    @staticmethod
    def from_json(item: JsonObj) -> JsonValue:
        return JsonValue(_Private(), Coproduct.inr(Coproduct.inl(item)))

    @staticmethod
    def from_list(item: FrozenList[JsonValue]) -> JsonValue:
        return JsonValue(_Private(), Coproduct.inr(Coproduct.inr(item)))
