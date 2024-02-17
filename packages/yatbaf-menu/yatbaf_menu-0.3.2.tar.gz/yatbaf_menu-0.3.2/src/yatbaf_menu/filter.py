from __future__ import annotations

__all__ = ("CallbackPayload",)

from typing import TYPE_CHECKING
from typing import final

if TYPE_CHECKING:
    from yatbaf.types import CallbackQuery


@final
class CallbackPayload:
    __slots__ = (
        "payload",
        "priority",
    )

    def __init__(self, payload: str) -> None:
        self.payload = payload
        self.priority = 300

    def check(self, q: CallbackQuery) -> bool:
        return q.data[:8] == self.payload  # type: ignore[index]
