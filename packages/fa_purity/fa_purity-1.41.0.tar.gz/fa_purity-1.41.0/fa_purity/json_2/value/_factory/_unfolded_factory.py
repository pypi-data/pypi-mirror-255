from . import (
    _common,
)
from ._jval_factory import (
    JsonValueFactory,
)
from dataclasses import (
    dataclass,
)
from fa_purity.frozen import (
    FrozenDict,
    FrozenList,
)
from fa_purity.json_2.primitive import (
    Primitive,
)
from fa_purity.json_2.value._core import (
    JsonObj,
    JsonValue,
    UnfoldedJVal,
)
from fa_purity.result import (
    Result,
)
from fa_purity.result.core import (
    ResultE,
)
from fa_purity.result.factory import (
    ResultFactory,
)
from fa_purity.utils import (
    cast_exception,
)
from typing import (
    Any,
    Dict,
    IO,
    List,
    Union,
)


def _only_json_objs(value: JsonValue) -> ResultE[JsonObj]:
    _factory: ResultFactory[JsonObj, Exception] = ResultFactory()
    return value.map(
        lambda _: _factory.failure(
            ValueError("Expected `JsonObj` not `JsonPrimitive`")
        ).alt(cast_exception),
        lambda _: _factory.failure(
            ValueError("Expected `JsonObj` not `FrozenList[JsonValue]`")
        ).alt(cast_exception),
        lambda d: _factory.success(d),
    )


@dataclass(frozen=True)
class UnfoldedFactory:
    "Factory of unfolded `JsonValue` objects"

    @staticmethod
    def from_list(
        raw: Union[List[Primitive], FrozenList[Primitive]]
    ) -> FrozenList[JsonValue]:
        return _common.from_list(raw)

    @staticmethod
    def from_dict(
        raw: Union[Dict[str, Primitive], FrozenDict[str, Primitive]]
    ) -> JsonObj:
        return _common.from_dict(raw)

    @staticmethod
    def from_unfolded_dict(
        raw: Union[Dict[str, UnfoldedJVal], FrozenDict[str, UnfoldedJVal]]
    ) -> JsonObj:
        return FrozenDict(
            {
                key: JsonValueFactory.from_unfolded(val)
                for key, val in raw.items()
            }
        )

    @staticmethod
    def from_unfolded_list(
        raw: Union[List[UnfoldedJVal], FrozenList[UnfoldedJVal]]
    ) -> FrozenList[JsonValue]:
        return tuple(JsonValueFactory.from_unfolded(item) for item in raw)

    @staticmethod
    def from_raw_dict(raw: Dict[str, Any]) -> ResultE[JsonObj]:  # type: ignore[misc]
        err = Result.failure(
            cast_exception(TypeError("Not a `JsonObj`")), JsonObj
        )
        return JsonValueFactory.from_any(raw).bind(  # type: ignore[misc]
            lambda jv: jv.map(
                lambda _: err,
                lambda _: err,
                lambda x: Result.success(x),
            )
        )

    @staticmethod
    def loads(raw: str) -> ResultE[JsonObj]:
        return JsonValueFactory.json_value_loads(raw).bind(_only_json_objs)

    @staticmethod
    def load(raw: IO[str]) -> ResultE[JsonObj]:
        return JsonValueFactory.json_value_load(raw).bind(_only_json_objs)
