from decimal import (
    Decimal,
)
from fa_purity.frozen import (
    freeze,
)
from fa_purity.json import (
    JsonValue as LegacyJsonValue,
)
from fa_purity.json.transform import (
    dumps as legacy_dumps,
)
from fa_purity.json_2 import (
    JsonPrimitiveFactory,
    JsonValue,
    Unfolder,
)


def test_legacy_json() -> None:
    obj = freeze({"foo": LegacyJsonValue(Decimal("123.44"))})
    assert legacy_dumps(obj)


def test_json_2() -> None:
    obj = freeze(
        {
            "foo": JsonValue.from_primitive(
                JsonPrimitiveFactory.from_raw(Decimal("123.44"))
            )
        }
    )
    assert Unfolder.dumps(obj)
