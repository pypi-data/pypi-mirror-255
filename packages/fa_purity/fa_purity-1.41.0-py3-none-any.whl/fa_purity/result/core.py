from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from fa_purity._core.result import (
    PureResult,
)
from fa_purity.union import (
    Coproduct,
    CoproductTransform,
)
from fa_purity.utils import (
    raise_exception,
)
from typing import (
    Callable,
    Generic,
    NoReturn,
    Optional,
    Type,
    TypeVar,
    Union,
)

_S = TypeVar("_S")
_F = TypeVar("_F")
_T = TypeVar("_T")


@dataclass(frozen=True)
class UnwrapError(Exception, Generic[_S, _F]):
    # DO NOT catch specific `UnwrapError[_S, _F]` error
    # catch always `UnwrapError`
    container: "Result[_S, _F]"


@dataclass(frozen=True)
class Result(Generic[_S, _F]):
    _inner: PureResult[_S, _F]

    @staticmethod
    def success(val: _S, _type: Optional[Type[_F]] = None) -> Result[_S, _F]:
        return Result(PureResult.success(val, _type))

    @staticmethod
    def failure(val: _F, _type: Optional[Type[_S]] = None) -> Result[_S, _F]:
        return Result(PureResult.failure(val, _type))

    def pure_result(self) -> PureResult[_S, _F]:
        return self._inner

    def map(self, function: Callable[[_S], _T]) -> Result[_T, _F]:
        return Result(self._inner.map(function))

    def alt(self, function: Callable[[_F], _T]) -> Result[_S, _T]:
        return Result(self._inner.alt(function))

    def to_coproduct(self) -> Coproduct[_S, _F]:
        return self._inner.to_coproduct()

    def bind(self, function: Callable[[_S], Result[_T, _F]]) -> Result[_T, _F]:
        return Result(self._inner.bind(lambda x: function(x).pure_result()))

    def lash(self, function: Callable[[_F], Result[_S, _T]]) -> Result[_S, _T]:
        return Result(self._inner.lash(lambda x: function(x).pure_result()))

    def swap(self) -> Result[_F, _S]:
        return Result(self._inner.swap())

    def apply(self, wrapped: Result[Callable[[_S], _T], _F]) -> Result[_T, _F]:
        return wrapped.bind(lambda f: self.map(f))

    def cop_value_or(self, default: _T) -> Coproduct[_S, _T]:
        return self._inner.cop_value_or(default)

    def cop_or_else_call(
        self, function: Callable[[], _T]
    ) -> Coproduct[_S, _T]:
        return self._inner.cop_or_else_call(function)

    def value_or(self, default: _T) -> Union[_S, _T]:
        return CoproductTransform(self.cop_value_or(default)).to_union()

    def or_else_call(self, function: Callable[[], _T]) -> Union[_S, _T]:
        return CoproductTransform(self.cop_or_else_call(function)).to_union()

    def to_union(self) -> Union[_S, _F]:
        return self._inner.to_union()

    def unwrap(self) -> Union[_S, NoReturn]:
        return self._inner.map(lambda s: s).or_else_call(
            lambda: raise_exception(UnwrapError(self))
        )

    def unwrap_fail(self) -> Union[_F, NoReturn]:
        return (
            self._inner.swap()
            .map(lambda f: f)
            .or_else_call(lambda: raise_exception(UnwrapError(self)))
        )


ResultE = Result[_T, Exception]  # type: ignore[misc]
PureResultE = PureResult[_T, Exception]  # type: ignore[misc]

__all__ = [
    "PureResult",
    "PureResultE",
]
