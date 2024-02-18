from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from fa_purity._bug import (
    LibraryBug,
)
from typing import (
    Callable,
    Generic,
    TypeVar,
    Union,
)

_L = TypeVar("_L")
_R = TypeVar("_R")
_T = TypeVar("_T")


@dataclass(frozen=True)
class _Empty:
    pass


@dataclass(frozen=True)
class _Coproduct(Generic[_L, _R]):
    left: Union[_L, _Empty]
    right: Union[_R, _Empty]
    left_val: bool

    @staticmethod
    def assert_non_empty(item: Union[_T, _Empty]) -> _T:
        if isinstance(item, _Empty):
            raise LibraryBug(
                ValueError("assert_non_empty received empty input")
            )
        return item


@dataclass(frozen=True)
class Coproduct(Generic[_L, _R]):
    _inner: _Coproduct[_L, _R]

    @staticmethod
    def inl(value: _L) -> Coproduct[_L, _R]:
        return Coproduct(_Coproduct(value, _Empty(), True))

    @staticmethod
    def inr(value: _R) -> Coproduct[_L, _R]:
        return Coproduct(_Coproduct(_Empty(), value, False))

    def map(
        self, transform_1: Callable[[_L], _T], transform_2: Callable[[_R], _T]
    ) -> _T:
        if self._inner.left_val:
            return transform_1(_Coproduct.assert_non_empty(self._inner.left))
        return transform_2(_Coproduct.assert_non_empty(self._inner.right))


@dataclass(frozen=True)
class CoproductFactory(Generic[_L, _R]):
    def inl(self, value: _L) -> Coproduct[_L, _R]:
        return Coproduct.inl(value)

    def inr(self, value: _R) -> Coproduct[_L, _R]:
        return Coproduct.inr(value)
