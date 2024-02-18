from fa_purity._core.result import (
    PureResult,
)
from fa_purity.frozen import (
    FrozenList,
)
from fa_purity.utils import (
    raise_exception,
)


def test_all_ok() -> None:
    success: FrozenList[PureResult[int, str]] = (
        PureResult.success(1),
        PureResult.success(2),
    )
    assert (
        PureResult.all_ok(success)
        .alt(
            lambda _: raise_exception(Exception("failure"))  # type: ignore[misc]
        )
        .to_union()
    )
    failure: FrozenList[PureResult[int, str]] = (
        PureResult.success(1),
        PureResult.failure("foo"),
    )
    assert (
        PureResult.all_ok(failure)
        .swap()
        .alt(
            lambda _: raise_exception(Exception("not failure"))  # type: ignore[misc]
        )
        .to_union()
    )
