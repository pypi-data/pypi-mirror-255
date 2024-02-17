from __future__ import annotations

__all__ = ("Payload",)

from itertools import product
from string import ascii_letters
from string import digits


class Payload:
    __slots__ = (
        "_bucket",
        "_prefix",
    )

    def __init__(self, prefix: str = "") -> None:
        self._bucket = product(f"{ascii_letters}{digits}", repeat=2).__next__
        self._prefix = prefix

    @property
    def prefix(self) -> str:
        return self._prefix

    def get(self) -> str:
        return f"{self._prefix}{''.join(self._bucket())}"
