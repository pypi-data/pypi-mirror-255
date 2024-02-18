from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
    field,
)
from decimal import (
    Decimal,
)
from fa_purity.union import (
    Coproduct,
)
from typing import (
    Callable,
    TypeVar,
)

_T = TypeVar("_T")

_bool_or_none = Coproduct[bool, None]
_decimal_or = Coproduct[Decimal, _bool_or_none]
_float_or = Coproduct[float, _decimal_or]
_int_or = Coproduct[int, _float_or]
_JsonPrimitive = Coproduct[str, _int_or]


@dataclass(frozen=True)
class _Private:
    pass


@dataclass(frozen=True)
class JsonPrimitive:
    "The type for primitive objects in a json"
    _private: _Private = field(repr=False, hash=False, compare=False)
    _value: _JsonPrimitive

    def map(
        self,
        str_case: Callable[[str], _T],
        int_case: Callable[[int], _T],
        float_case: Callable[[float], _T],
        decimal_case: Callable[[Decimal], _T],
        bool_case: Callable[[bool], _T],
        none_case: Callable[[], _T],
    ) -> _T:
        return self._value.map(
            str_case,
            lambda a: a.map(
                int_case,
                lambda b: b.map(
                    float_case,
                    lambda c: c.map(
                        decimal_case,
                        lambda d: d.map(bool_case, lambda _: none_case()),
                    ),
                ),
            ),
        )

    @staticmethod
    def from_str(item: str) -> JsonPrimitive:
        return JsonPrimitive(_Private(), Coproduct.inl(item))

    @staticmethod
    def from_int(item: int) -> JsonPrimitive:
        return JsonPrimitive(_Private(), Coproduct.inr(Coproduct.inl(item)))

    @staticmethod
    def from_float(item: float) -> JsonPrimitive:
        return JsonPrimitive(
            _Private(), Coproduct.inr(Coproduct.inr(Coproduct.inl(item)))
        )

    @staticmethod
    def from_decimal(item: Decimal) -> JsonPrimitive:
        return JsonPrimitive(
            _Private(),
            Coproduct.inr(Coproduct.inr(Coproduct.inr(Coproduct.inl(item)))),
        )

    @staticmethod
    def from_bool(item: bool) -> JsonPrimitive:
        return JsonPrimitive(
            _Private(),
            Coproduct.inr(
                Coproduct.inr(
                    Coproduct.inr(Coproduct.inr(Coproduct.inl(item)))
                )
            ),
        )

    @staticmethod
    def empty() -> JsonPrimitive:
        return JsonPrimitive(
            _Private(),
            Coproduct.inr(
                Coproduct.inr(
                    Coproduct.inr(Coproduct.inr(Coproduct.inr(None)))
                )
            ),
        )
