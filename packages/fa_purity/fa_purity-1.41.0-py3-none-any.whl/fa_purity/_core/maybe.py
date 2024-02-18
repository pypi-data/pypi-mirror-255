from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from fa_purity._core.result import (
    PureResult,
)
from typing import (
    Callable,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
)

_A = TypeVar("_A")
_B = TypeVar("_B")


@dataclass(frozen=True)
class PureMaybe(Generic[_A]):
    "Equivalent to PureResult[_A, None], but designed to handle possible empty values"
    _value: PureResult[_A, None]

    @staticmethod
    def some(value: _A) -> PureMaybe[_A]:
        return PureMaybe(PureResult.success(value))

    @staticmethod
    def empty(_type: Optional[Type[_A]] = None) -> PureMaybe[_A]:
        return PureMaybe.from_optional(None)

    @staticmethod
    def from_optional(value: Optional[_A]) -> PureMaybe[_A]:
        if value is None:
            return PureMaybe(PureResult.failure(value))
        return PureMaybe(PureResult.success(value))

    @staticmethod
    def from_result(result: PureResult[_A, None]) -> PureMaybe[_A]:
        return PureMaybe(result)

    def to_result(self) -> PureResult[_A, None]:
        return self._value

    def map(self, function: Callable[[_A], _B]) -> PureMaybe[_B]:
        return PureMaybe(self._value.map(function))

    def bind(self, function: Callable[[_A], PureMaybe[_B]]) -> PureMaybe[_B]:
        return PureMaybe(self._value.bind(lambda a: function(a).to_result()))

    def bind_optional(
        self, function: Callable[[_A], Optional[_B]]
    ) -> PureMaybe[_B]:
        return self.bind(lambda a: PureMaybe.from_optional(function(a)))

    def lash(self, function: Callable[[], PureMaybe[_A]]) -> PureMaybe[_A]:
        return PureMaybe(self._value.lash(lambda _: function().to_result()))

    def value_or(self, default: _B) -> Union[_A, _B]:
        return self._value.value_or(default)

    def or_else_call(self, function: Callable[[], _B]) -> Union[_A, _B]:
        return self._value.or_else_call(function)
