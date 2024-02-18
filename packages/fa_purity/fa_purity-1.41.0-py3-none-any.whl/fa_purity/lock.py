from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
)
from fa_purity._core.cmd import (
    Cmd,
    CmdUnwrapper,
)
from threading import (
    Lock as _Lock,
)
from typing import (
    TypeVar,
)

_T = TypeVar("_T")


@dataclass(frozen=True)
class ThreadLock:
    _inner: _Lock

    @staticmethod
    def new() -> Cmd[ThreadLock]:
        return Cmd.from_cmd(lambda: ThreadLock(_Lock()))

    def execute_with_lock(self, cmd: Cmd[_T]) -> Cmd[_T]:
        def _action(unwrapper: CmdUnwrapper) -> _T:
            with self._inner:
                return unwrapper.act(cmd)

        return Cmd.new_cmd(_action)

    @property
    def acquire(self) -> Cmd[None]:
        return Cmd.from_cmd(lambda: self._inner.acquire()).map(lambda _: None)

    @property
    def try_acquire(self) -> Cmd[bool]:
        "return False if not acquired"
        return Cmd.from_cmd(lambda: self._inner.acquire(False))

    @property
    def release(self) -> Cmd[None]:
        return Cmd.from_cmd(lambda: self._inner.release()).map(lambda _: None)

    @property
    def locked(self) -> Cmd[bool]:
        return Cmd.from_cmd(lambda: self._inner.locked())
