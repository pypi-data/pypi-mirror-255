from arch_lint.dag import (
    DagMap,
)
from arch_lint.graph import (
    FullPathModule,
)
from fa_purity import (
    FrozenList,
)
from typing import (
    Dict,
    FrozenSet,
    TypeVar,
    Union,
)

_dag: Dict[str, FrozenList[Union[FrozenList[str], str]]] = {
    "fa_purity": (
        "flatten",
        "stream",
        ("json_2", "date_time"),
        (
            "pure_iter",
            "json",
        ),
        "_iter_factory",
        "maybe",
        ("lock", "cmd", "result"),
        "union",
        "_core",
        "frozen",
        ("_bug", "utils"),
    ),
    "fa_purity._core": ("maybe", "result", ("cmd", "coproduct")),
    "fa_purity._core.coproduct": ("_transform", "_core"),
    "fa_purity.stream": (
        "transform",
        "factory",
        "core",
        "_inner",
    ),
    "fa_purity.pure_iter": (
        "transform",
        "factory",
        "core",
        "_inner",
    ),
    "fa_purity.result": (
        "transform",
        "factory",
        "core",
    ),
    "fa_purity.cmd": (
        "transform",
        "core",
    ),
    "fa_purity.json_2": (
        "value",
        "primitive",
    ),
    "fa_purity.json_2.primitive": (
        ("_transform", "_factory"),
        "_core",
    ),
    "fa_purity.json_2.value": (
        ("_transform", "_factory"),
        "_core",
    ),
    "fa_purity.json_2.value._factory": (
        "_unfolded_factory",
        "_jval_factory",
        "_common",
    ),
    "fa_purity.json": (
        "transform",
        "factory",
        "value",
        "primitive",
        "errors",
    ),
    "fa_purity.json.primitive": (
        "factory",
        "core",
    ),
    "fa_purity.json.value": (
        "transform",
        "factory",
        "core",
    ),
}
_T = TypeVar("_T")


def raise_or_return(item: Union[Exception, _T]) -> _T:
    if isinstance(item, Exception):
        raise item
    return item


def project_dag() -> DagMap:
    return raise_or_return(DagMap.new(_dag))


def forbidden_allowlist() -> Dict[FullPathModule, FrozenSet[FullPathModule]]:
    _raw: Dict[str, FrozenSet[str]] = {}
    return {
        raise_or_return(FullPathModule.from_raw(k)): frozenset(
            raise_or_return(FullPathModule.from_raw(i)) for i in v
        )
        for k, v in _raw.items()
    }
