from deprecated import (
    deprecated,
)
from fa_purity._core.cmd import (
    Cmd,
    CmdUnwrapper,
    unsafe_unwrap,
)
from typing import (
    Callable,
    TypeVar,
)

_A = TypeVar("_A")


@deprecated("NEW API: use `Cmd.new_cmd` instead")  # type: ignore[misc]
def new_cmd(action: Callable[[CmdUnwrapper], _A]) -> Cmd[_A]:
    return Cmd.new_cmd(action)


__all__ = [
    "Cmd",
    "CmdUnwrapper",
    "unsafe_unwrap",
]
