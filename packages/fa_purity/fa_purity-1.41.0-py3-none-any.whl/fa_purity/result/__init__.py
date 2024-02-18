from .core import (
    Result,
    ResultE,
    UnwrapError,
)
from .factory import (
    ResultFactory,
)
from fa_purity._core.result import (
    PureResult,
    PureResultFactory,
)

__all__ = [
    "PureResult",
    "PureResultFactory",
    "UnwrapError",
    "Result",
    "ResultE",
    "ResultFactory",
]
