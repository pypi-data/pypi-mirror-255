from ._core import (
    JsonPrimitive,
)
from dataclasses import (
    dataclass,
)
from decimal import (
    Decimal,
)
from fa_purity.result import (
    Result,
)
from fa_purity.result.core import (
    ResultE,
)
from fa_purity.utils import (
    cast_exception,
)
from typing import (
    Optional,
    TypeVar,
    Union,
)

_T = TypeVar("_T")
Primitive = Union[str, int, float, Decimal, bool, None]


@dataclass(frozen=True)
class JsonPrimitiveFactory:
    "Factory of `JsonPrimitive` objects"

    @staticmethod
    def from_any(
        raw: Optional[_T],
    ) -> ResultE[JsonPrimitive]:
        if raw is None:
            return Result.success(JsonPrimitive.empty())
        if isinstance(raw, bool):
            return Result.success(JsonPrimitive.from_bool(raw))
        if isinstance(raw, str):
            return Result.success(JsonPrimitive.from_str(raw))
        if isinstance(raw, int):
            return Result.success(JsonPrimitive.from_int(raw))
        if isinstance(raw, float):
            return Result.success(JsonPrimitive.from_float(raw))
        if isinstance(raw, Decimal):
            return Result.success(JsonPrimitive.from_decimal(raw))
        return Result.failure(
            cast_exception(TypeError("Cannot convert to `JsonPrimitive`"))
        )

    @staticmethod
    def from_raw(raw: Primitive) -> JsonPrimitive:
        if raw is None:
            return JsonPrimitive.empty()
        if isinstance(raw, bool):
            return JsonPrimitive.from_bool(raw)
        if isinstance(raw, str):
            return JsonPrimitive.from_str(raw)
        if isinstance(raw, int):
            return JsonPrimitive.from_int(raw)
        if isinstance(raw, float):
            return JsonPrimitive.from_float(raw)
        if isinstance(raw, Decimal):
            return JsonPrimitive.from_decimal(raw)
