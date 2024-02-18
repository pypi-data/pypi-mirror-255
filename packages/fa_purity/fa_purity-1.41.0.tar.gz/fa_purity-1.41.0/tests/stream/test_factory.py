from fa_purity._core.cmd import (
    Cmd,
)
from fa_purity.cmd import (
    unsafe_unwrap,
)
from fa_purity.maybe import (
    Maybe,
)
from fa_purity.pure_iter.factory import (
    from_range,
)
from fa_purity.stream.factory import (
    StreamFactory,
)
from tests.stream._utils import (
    assert_different_iter,
    rand_int,
)


def test_from_commands() -> None:
    items = from_range(range(10)).map(lambda _: rand_int())
    stm = StreamFactory.from_commands(items)
    assert_different_iter(stm)


def test_generate() -> None:
    def _cmd(prev: int) -> Cmd[int]:
        return Cmd.from_cmd(lambda: prev + 1)

    stm = StreamFactory.generate(
        _cmd, lambda x: Maybe.from_optional(None if x >= 9 else x), 0
    )
    assert_different_iter(stm)
    assert unsafe_unwrap(stm.to_list()) == tuple(range(1, 10))
