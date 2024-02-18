from dataclasses import (
    dataclass,
)
from deprecated import (
    deprecated,
)
from fa_purity.frozen import (
    freeze,
)
from fa_purity.json import (
    JsonObj as LegacyJsonObj,
    JsonValue as LegacyJsonValue,
)
from fa_purity.json_2.primitive import (
    JsonPrimitive,
    JsonPrimitiveFactory,
    JsonPrimitiveUnfolder,
    Primitive,
)
from fa_purity.json_2.value import (
    JsonObj,
    JsonUnfolder,
    JsonValue,
    JsonValueFactory,
    UnfoldedFactory,
    Unfolder,
)


@deprecated("Temporal adapter for `json` -> `json_2` migration")  # type: ignore[misc]
@dataclass(frozen=True)
class LegacyAdapter:
    @classmethod
    def json_value(cls, legacy: LegacyJsonValue) -> JsonValue:
        return legacy.map(
            lambda p: JsonValue.from_primitive(
                JsonPrimitiveFactory.from_raw(p)
            ),
            lambda items: JsonValue.from_list(
                tuple(cls.json_value(i) for i in items)
            ),
            lambda d: JsonValue.from_json(
                freeze({k: cls.json_value(v) for k, v in d.items()})
            ),
        )

    @classmethod
    def json(cls, legacy: LegacyJsonObj) -> JsonObj:
        _new = {k: cls.json_value(v) for k, v in legacy.items()}
        return freeze(_new)

    @classmethod
    def to_legacy_value(cls, value: JsonValue) -> LegacyJsonValue:
        return value.map(
            lambda p: p.map(
                lambda x: LegacyJsonValue(x),
                lambda x: LegacyJsonValue(x),
                lambda x: LegacyJsonValue(x),
                lambda x: LegacyJsonValue(x),
                lambda x: LegacyJsonValue(x),
                lambda: LegacyJsonValue(None),
            ),
            lambda items: LegacyJsonValue(
                tuple(cls.to_legacy_value(i) for i in items)
            ),
            lambda d: LegacyJsonValue(
                freeze({k: cls.to_legacy_value(v) for k, v in d.items()})
            ),
        )

    @classmethod
    def to_legacy_json(cls, value: JsonObj) -> LegacyJsonObj:
        _new = {k: cls.to_legacy_value(v) for k, v in value.items()}
        return freeze(_new)


__all__ = [
    "JsonValue",
    "JsonObj",
    "JsonValueFactory",
    "JsonUnfolder",
    "UnfoldedFactory",
    "Unfolder",
    "Primitive",
    "JsonPrimitive",
    "JsonPrimitiveFactory",
    "JsonPrimitiveUnfolder",
]
