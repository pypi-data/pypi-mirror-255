from fa_purity.frozen import (
    freeze,
)
from fa_purity.json_2.primitive import (
    JsonPrimitiveFactory,
    Primitive,
)
from fa_purity.json_2.value import (
    JsonValue,
    JsonValueFactory,
    Unfolder,
)


def _prim_value(value: Primitive) -> JsonValue:
    return JsonValue.from_primitive(JsonPrimitiveFactory.from_raw(value))


def test_from_any() -> None:
    json_obj = freeze(
        {
            "foo": JsonValue.from_json(
                freeze(
                    {
                        "nested": JsonValue.from_list(
                            tuple([_prim_value("hi"), _prim_value(99)])
                        ),
                    }
                )
            )
        }
    )
    json_obj_from_raw = (
        JsonValueFactory.from_any({"foo": {"nested": ["hi", 99]}})
        .bind(Unfolder.to_json)
        .unwrap()
    )
    assert json_obj == json_obj_from_raw
