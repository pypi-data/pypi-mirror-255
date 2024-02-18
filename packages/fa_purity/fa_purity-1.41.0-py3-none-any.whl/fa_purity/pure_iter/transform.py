from dataclasses import (
    dataclass,
)
from fa_purity import (
    _iter_factory,
)
from fa_purity.cmd import (
    Cmd,
)
from fa_purity.cmd.core import (
    CmdUnwrapper,
)
from fa_purity.maybe import (
    Maybe,
)
from fa_purity.pure_iter.core import (
    PureIter,
)
from fa_purity.pure_iter.factory import (
    unsafe_from_cmd,
)
from typing import (
    Optional,
    TypeVar,
)

_T = TypeVar("_T")


@dataclass(frozen=True)
class PureIterTransform:
    "`PureIter` common transforms"

    @staticmethod
    def chain(
        unchained: PureIter[PureIter[_T]],
    ) -> PureIter[_T]:
        return unchained.bind(lambda x: x)

    @staticmethod
    def consume(p_iter: PureIter[Cmd[None]]) -> Cmd[None]:
        def _action(unwrapper: CmdUnwrapper) -> None:
            for c in p_iter:
                unwrapper.act(c)

        return Cmd.new_cmd(_action)

    @staticmethod
    def filter_opt(items: PureIter[Optional[_T]]) -> PureIter[_T]:
        return unsafe_from_cmd(
            Cmd.from_cmd(lambda: _iter_factory.filter_none(items))
        )

    @classmethod
    def filter_maybe(cls, items: PureIter[Maybe[_T]]) -> PureIter[_T]:
        return cls.filter_opt(items.map(lambda x: x.value_or(None)))

    @staticmethod
    def until_none(items: PureIter[Optional[_T]]) -> PureIter[_T]:
        return unsafe_from_cmd(
            Cmd.from_cmd(lambda: _iter_factory.until_none(items))
        )

    @classmethod
    def until_empty(cls, items: PureIter[Maybe[_T]]) -> PureIter[_T]:
        return cls.until_none(items.map(lambda m: m.value_or(None)))


chain = PureIterTransform.chain
consume = PureIterTransform.consume
filter_opt = PureIterTransform.filter_opt
filter_maybe = PureIterTransform.filter_maybe
until_none = PureIterTransform.until_none
until_empty = PureIterTransform.until_empty
