from fa_purity._core.result import (
    PureResult,
)
from fa_purity.frozen import (
    FrozenList,
)
from fa_purity.result.core import (
    Result,
)
from fa_purity.result.factory import (
    ResultFactory,
)
from typing import (
    TypeVar,
)

_S = TypeVar("_S")
_F = TypeVar("_F")


def all_ok(items: FrozenList[Result[_S, _F]]) -> Result[FrozenList[_S], _F]:
    result = PureResult.all_ok(tuple(i.pure_result() for i in items))
    factory: ResultFactory[FrozenList[_S], _F] = ResultFactory()
    return (
        result.map(lambda s: factory.success(s))
        .alt(lambda f: factory.failure(f))
        .to_union()
    )
