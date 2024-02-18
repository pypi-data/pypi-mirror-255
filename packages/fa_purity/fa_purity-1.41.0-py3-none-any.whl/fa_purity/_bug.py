from dataclasses import (
    dataclass,
)
from typing import (
    NoReturn,
)


@dataclass(frozen=True)
class LibraryBug(Exception):
    traceback: Exception

    def __str__(self) -> str:
        return f"If raised then there is a bug in the `fa_purity` library"
