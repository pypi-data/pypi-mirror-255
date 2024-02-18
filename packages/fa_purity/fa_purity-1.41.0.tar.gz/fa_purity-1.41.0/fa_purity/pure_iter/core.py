from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from fa_purity import (
    _iter_factory,
)
from fa_purity.cmd import (
    unsafe_unwrap,
)
from fa_purity.cmd.core import (
    Cmd,
)
from fa_purity.frozen import (
    FrozenList,
)
from fa_purity.maybe import (
    Maybe,
)
from fa_purity.pure_iter._inner import (
    InnerPureIter,
)
import functools
from typing import (
    Callable,
    Generic,
    Iterator,
    Tuple,
    TypeVar,
)

_T = TypeVar("_T")
_R = TypeVar("_R")
_S = TypeVar("_S")


@dataclass(frozen=True)
class PureIter(Generic[_T]):
    # unsafe_unwrap use is safe due to iters equivalence
    _inner: InnerPureIter[_T]

    def generate(
        self, function: Callable[[_S, _T], Tuple[_S, _R]], init_state: _S
    ) -> PureIter[_R]:
        """
        Apply the function over each item.
        The argument state (_S) comes from a previous computation of the function over
        a previous state-item pair or from `init_state` if is the first element.
        """
        draft: InnerPureIter[_R] = InnerPureIter(
            self._inner.new_iter.map(
                lambda i: _iter_factory.gen_next(function, init_state, i)
            )
        )
        return PureIter(draft)

    def enumerate(self, init: int) -> PureIter[Tuple[int, _T]]:
        return self.generate(lambda i, t: (i + 1, (i, t)), init)

    def map(self, function: Callable[[_T], _R]) -> PureIter[_R]:
        return self.generate(lambda _, t: (None, function(t)), None)

    def reduce(self, function: Callable[[_R, _T], _R], init: _R) -> _R:
        return unsafe_unwrap(
            self._inner.new_iter.map(
                lambda i: functools.reduce(function, i, init)
            )
        )

    def bind(self, function: Callable[[_T], PureIter[_R]]) -> PureIter[_R]:
        unchained = self.map(function)
        draft: InnerPureIter[_R] = InnerPureIter(
            Cmd.from_cmd(lambda: _iter_factory.chain(unchained))
        )
        return PureIter(draft)

    def filter(self, function: Callable[[_T], bool]) -> PureIter[_T]:
        draft = InnerPureIter(
            self._inner.new_iter.map(lambda i: iter(filter(function, i)))
        )
        return PureIter(draft)

    def find_first(self, criteria: Callable[[_T], bool]) -> Maybe[_T]:
        result = self._inner.new_iter.map(
            lambda i: _iter_factory.find_first(criteria, i)
        ).map(lambda x: Maybe.from_optional(x))
        return unsafe_unwrap(result)

    def chunked(self, size: int) -> PureIter[FrozenList[_T]]:
        draft = InnerPureIter(
            self._inner.new_iter.map(lambda i: _iter_factory.chunked(i, size))
        )
        return PureIter(draft)

    def to_list(self) -> FrozenList[_T]:
        return tuple(self)

    def transform(self, function: Callable[[PureIter[_T]], _R]) -> _R:
        return function(self)

    def __iter__(self) -> Iterator[_T]:
        return iter(unsafe_unwrap(self._inner.new_iter))
