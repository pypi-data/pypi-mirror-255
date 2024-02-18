from ._inner import (
    InnerStream,
)
from dataclasses import (
    dataclass,
)
from fa_purity import (
    _iter_factory,
)
from fa_purity._core.cmd import (
    CmdUnwrapper,
)
from fa_purity.cmd import (
    Cmd,
)
from fa_purity.maybe import (
    Maybe,
)
from fa_purity.pure_iter.core import (
    PureIter,
)
from fa_purity.stream.core import (
    Stream,
)
from typing import (
    Callable,
    Iterable,
    TypeVar,
)

_T = TypeVar("_T")
_S = TypeVar("_S")


def unsafe_from_cmd(cmd: Cmd[Iterable[_T]]) -> Stream[_T]:
    # [WARNING] unsafe constructor
    # - Type-check cannot ensure its proper use
    # - Do not use until is strictly necessary
    # - Do unit test over the function defined by this
    #
    # As with `PureIter unsafe_from_cmd` the cmd must return a new iterable
    # object in each call to ensure that the stream is never consumed,
    # nevertheless they can be semanticly different iterables.
    return Stream(InnerStream(cmd))


@dataclass(frozen=True)
class StreamFactory:
    @staticmethod
    def from_commands(piter: PureIter[Cmd[_T]]) -> Stream[_T]:
        items = InnerStream(_iter_factory.squash(piter))
        return Stream(items)

    @staticmethod
    def generate(
        get: Callable[[_S], Cmd[_T]],
        extract: Callable[[_T], Maybe[_S]],
        init: _S,
    ) -> Stream[_T]:
        """
        Generate a `Stream` from a command that depends on a previous state
        that depends from the result of the previous stream command.

        - `get` = the command that depends on a previous state
        - `extract` = how to derive the state from the result of the previous command.
            This also determines the stream end when returning empty.
        - `init` = initial state value

        """

        def _iter(unwrapper: CmdUnwrapper) -> Iterable[_T]:
            state: Maybe[_S] = Maybe.from_value(init)
            while state.map(lambda _: True).value_or(False):
                item = unwrapper.act(get(state.unwrap()))
                yield item
                state = extract(item)

        return unsafe_from_cmd(Cmd.new_cmd(_iter))


from_piter = StreamFactory.from_commands
