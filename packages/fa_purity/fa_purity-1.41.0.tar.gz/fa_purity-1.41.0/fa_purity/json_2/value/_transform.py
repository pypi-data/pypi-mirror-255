from ._core import (
    JsonObj,
    JsonValue,
)
from dataclasses import (
    dataclass,
)
from deprecated import (
    deprecated,
)
from fa_purity.frozen import (
    FrozenDict,
    FrozenList,
    unfreeze,
)
from fa_purity.json_2.primitive import (
    JsonPrimitive,
    JsonPrimitiveUnfolder,
    Primitive,
)
from fa_purity.maybe import (
    Maybe,
)
from fa_purity.pure_iter import (
    PureIterFactory,
)
from fa_purity.result import (
    Result,
)
from fa_purity.result.core import (
    ResultE,
)
from fa_purity.result.factory import (
    try_get,
)
from fa_purity.result.transform import (
    all_ok,
)
from fa_purity.union import (
    UnionFactory,
)
from fa_purity.utils import (
    cast_exception,
)
from simplejson import (
    dumps as _dumps,
    JSONEncoder,
)
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    TypeVar,
    Union,
)

_T = TypeVar("_T")


class _JsonEncoder(JSONEncoder):
    def default(self: JSONEncoder, o: _T) -> Any:  # type: ignore[misc]
        if isinstance(o, FrozenDict):
            return unfreeze(o)  # type: ignore[misc]
        if isinstance(o, JsonValue):
            result = o.map(
                lambda x: x.map(
                    lambda y: y,
                    lambda y: y,
                    lambda y: y,
                    lambda y: y,
                    lambda y: y,
                    lambda: None,
                ),
                lambda x: x,
                lambda x: x,
            )
            return result
        return JSONEncoder.default(self, o)  # type: ignore[misc]


def _transform_json(
    item: JsonObj, transform: Callable[[JsonValue], ResultE[_T]]
) -> ResultE[FrozenDict[str, _T]]:
    """"""
    key_values = (
        PureIterFactory.from_list(tuple(item.items()))
        .map(
            lambda t: transform(t[1])
            .map(lambda p: (t[0], p))
            .alt(
                lambda e: ValueError(f"key '{t[0]}' transform failed i.e. {e}")
            )
            .alt(cast_exception)
        )
        .to_list()
    )
    return all_ok(key_values).map(lambda x: FrozenDict(dict(x)))


@dataclass(frozen=True)
class Unfolder:
    "Common transforms to unfold `JsonValue` objects"

    @staticmethod
    def to_primitive(item: JsonValue) -> ResultE[JsonPrimitive]:
        "Transform to primitive"
        fail: ResultE[JsonPrimitive] = Result.failure(
            cast_exception(
                TypeError("Expected `JsonPrimitive` in unfolded `JsonValue`")
            )
        )
        return item.map(
            lambda x: Result.success(x),
            lambda _: fail,
            lambda _: fail,
        )

    @staticmethod
    def to_list(item: JsonValue) -> ResultE[FrozenList[JsonValue]]:
        "Transform to list"
        fail: ResultE[FrozenList[JsonValue]] = Result.failure(
            cast_exception(
                TypeError(
                    "Expected `FrozenList[JsonValue]` in unfolded `JsonValue`"
                )
            )
        )
        return item.map(
            lambda _: fail,
            lambda x: Result.success(x),
            lambda _: fail,
        )

    @staticmethod
    def to_json(item: JsonValue) -> ResultE[JsonObj]:
        "Transform to json"
        fail: ResultE[JsonObj] = Result.failure(
            cast_exception(
                TypeError("Expected `JsonObj` in unfolded `JsonValue`")
            )
        )
        return item.map(
            lambda _: fail,
            lambda _: fail,
            lambda x: Result.success(x),
        )

    @staticmethod
    def transform_list(
        items: FrozenList[JsonValue],
        transform: Callable[[JsonValue], ResultE[_T]],
    ) -> ResultE[FrozenList[_T]]:
        "Transform to list of `_T`"
        return all_ok(tuple(transform(i) for i in items))

    @staticmethod
    @deprecated("[Moved]: use `JsonUnfolder.map_values` instead")  # type: ignore[misc]
    def transform_json(
        item: JsonObj, transform: Callable[[JsonValue], ResultE[_T]]
    ) -> ResultE[FrozenDict[str, _T]]:
        "[DEPRECATED]"
        return _transform_json(item, transform)

    @staticmethod
    @deprecated("[Moved]: use `JsonUnfolder.dumps` instead")  # type: ignore[misc]
    def dumps(obj: JsonObj) -> str:
        "[DEPRECATED]"
        return _dumps(obj, cls=_JsonEncoder)  # type: ignore[misc]

    @classmethod
    def get(cls, item: JsonValue, key: str) -> ResultE[JsonValue]:
        "Transform into `JsonObj` and get an specific key value"
        return (
            cls.to_json(item)
            .alt(cast_exception)
            .bind(lambda d: try_get(d, key))
        )

    @classmethod
    def to_list_of(
        cls, item: JsonValue, transform: Callable[[JsonValue], ResultE[_T]]
    ) -> ResultE[FrozenList[_T]]:
        "Transform `JsonValue` into `FrozenList[_T]`"
        return cls.to_list(item).bind(
            lambda i: cls.transform_list(i, transform)
        )

    @classmethod
    def to_dict_of(
        cls, item: JsonValue, transform: Callable[[JsonValue], ResultE[_T]]
    ) -> ResultE[FrozenDict[str, _T]]:
        "Transform `JsonValue` into `FrozenDict[str, _T]`"
        return cls.to_json(item).bind(lambda i: _transform_json(i, transform))

    @staticmethod
    def extract_maybe(item: JsonValue) -> Maybe[JsonValue]:
        "If `JsonValue` is `None` return empty"
        to_none = (
            Unfolder.to_primitive(item)
            .bind(JsonPrimitiveUnfolder.to_none)
            .alt(lambda _: item)
        )
        return Maybe.from_result(to_none.swap())

    @classmethod
    def to_optional(
        cls, item: JsonValue, transform: Callable[[JsonValue], ResultE[_T]]
    ) -> ResultE[Optional[_T]]:
        "Transform `JsonValue` into `None` or `_T`"
        _union: UnionFactory[_T, None] = UnionFactory()
        return (
            cls.extract_maybe(item)
            .map(lambda v: transform(v).map(_union.inl))
            .value_or(Result.success(_union.inr(None), Exception))
        )

    @classmethod
    def to_raw(cls, value: JsonValue) -> Union[Dict[str, Any], List[Any], Primitive]:  # type: ignore[misc]
        "Transform to untyped raw json object"

        def _cast(item: Primitive) -> Primitive:
            # cast used for helping mypy to infer the correct return type
            return item

        return value.map(
            lambda p: p.map(
                lambda x: _cast(x),
                lambda x: _cast(x),
                lambda x: _cast(x),
                lambda x: _cast(x),
                lambda x: _cast(x),
                lambda: _cast(None),
            ),
            lambda items: [cls.to_raw(i) for i in items],  # type: ignore[misc]
            lambda dict_obj: {key: cls.to_raw(val) for key, val in dict_obj.items()},  # type: ignore[misc]
        )


@dataclass(frozen=True)
class JsonUnfolder:
    "Common transforms to unfold a `JsonObj`"

    @staticmethod
    def dumps(obj: JsonObj) -> str:
        "Transform into string format"
        return _dumps(obj, cls=_JsonEncoder)  # type: ignore[misc]

    @staticmethod
    def require(
        item: JsonObj, key: str, transform: Callable[[JsonValue], ResultE[_T]]
    ) -> ResultE[_T]:
        "Require some specific key on the `JsonObj`, if success apply the supplied transform"
        return (
            try_get(item, key)
            .bind(transform)
            .alt(
                lambda e: ValueError(
                    f"required key '{key}' unfold failed i.e. {e}"
                )
            )
            .alt(cast_exception)
        )

    @staticmethod
    def optional(
        item: JsonObj, key: str, transform: Callable[[JsonValue], ResultE[_T]]
    ) -> ResultE[Maybe[_T]]:
        """
        Get some specific key on the `JsonObj`
        - return empty if key is missing
        - return empty if value is `None`
        - else apply the supplied transform
        """
        empty: Maybe[_T] = Maybe.empty()

        return (
            (
                Maybe.from_result(try_get(item, key).alt(lambda _: None))
                .bind(Unfolder.extract_maybe)
                .map(lambda x: transform(x).map(lambda v: Maybe.from_value(v)))
                .value_or(Result.success(empty))
            )
            .alt(
                lambda e: ValueError(
                    f"optional key '{key}' unfold failed i.e. {e}"
                )
            )
            .alt(cast_exception)
        )

    @staticmethod
    def map_values(
        item: JsonObj, transform: Callable[[JsonValue], ResultE[_T]]
    ) -> ResultE[FrozenDict[str, _T]]:
        "Apply the transform to each value of the json"
        return _transform_json(item, transform)
