from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
    field,
)
from deprecated import (
    deprecated,
)
import sys
from typing import (
    Callable,
    Generic,
    NoReturn,
    TypeVar,
)

_A = TypeVar("_A")
_B = TypeVar("_B")


@dataclass(frozen=True)
class _Private:
    pass


@dataclass(frozen=True)
class Cmd(Generic[_A]):
    # Equivalent to haskell IO type
    # unsafe_unwrap not included as method for discouraging its use
    _value: Callable[[], _A]  # not a pure function!

    @staticmethod
    def from_cmd(value: Callable[[], _A]) -> Cmd[_A]:
        return Cmd(value)

    @staticmethod
    def new_cmd(action: Callable[[CmdUnwrapper], _A]) -> Cmd[_A]:
        return Cmd(lambda: action(_unwrapper))

    def map(self, function: Callable[[_A], _B]) -> Cmd[_B]:
        return Cmd(lambda: function(self._value()))

    def bind(self, function: Callable[[_A], Cmd[_B]]) -> Cmd[_B]:
        return Cmd(lambda: function(self._value())._value())

    def apply(self, wrapped: Cmd[Callable[[_A], _B]]) -> Cmd[_B]:
        return wrapped.bind(lambda f: self.map(f))

    def compute(self) -> NoReturn:
        self._value()
        sys.exit(0)

    def execute(self, _: _Private) -> _A:
        "Can not call this method, only authorized functions can execute a command e.g. unsafe_unwrap"
        return self._value()

    def __add__(self, other: Cmd[_B]) -> Cmd[_B]:
        return self.bind(lambda _: other)


@dataclass(frozen=True)
class CmdUnwrapper:
    """
    Object that brings a method that allows cmd execution,
    equivalent to `unsafe_unwrap`.

    Instances can not be created by the user by design.
    Only through the `Cmd.new_cmd` the user can use an
    instance of this type.
    """

    # Do not build any public constructors or instances
    # This obj is only accessible in the action context through the `new_cmd` builder
    _inner: _Private = field(repr=False, hash=False, compare=False)

    def act(self, action: Cmd[_A]) -> _A:
        """
        [WARNING] Not a pure function.

        This method is more safe than `unsafe_unwrap` since it
        wraps the result into another `Cmd`, but is possible to
        use it incorrectly in places where a pure function is
        expected e.g. `PureIter.map` and cause unexpected bugs.
        """
        return action.execute(_Private())

    @staticmethod
    @deprecated("DO NOT CALL: instead use the `act` method of a `CmdUnwrapper` instance")  # type: ignore[misc]
    def unwrap(action: Cmd[_A]) -> _A:
        return action.execute(_Private())


_unwrapper = CmdUnwrapper(_Private())


def unsafe_unwrap(action: Cmd[_A]) -> _A:
    # This is an unsafe constructor (type-check cannot ensure its proper use)
    # Do not use until is strictly necessary
    # WARNING: this is equivalent to compute, and will execute the Cmd
    #
    # Only use when all executions of the action (Cmd[_A]) result in the same
    # output instance (_A) and side effects are not present or negligible.
    # e.g. unwrap a cmd when used on a cached function definition
    #
    # [NOTICE] Do not use this function for defining a new Cmd, use `new_cmd` instead
    return action.execute(_Private())
