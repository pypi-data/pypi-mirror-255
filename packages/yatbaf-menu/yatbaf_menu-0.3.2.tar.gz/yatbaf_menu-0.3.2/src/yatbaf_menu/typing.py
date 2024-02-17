from __future__ import annotations

from typing import TYPE_CHECKING
from typing import TypeAlias

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable
    from collections.abc import Iterable

    from yatbaf.types import CallbackQuery
    from yatbaf.types import Message

Query: TypeAlias = "Message | CallbackQuery"
ChoiceItemsFn: TypeAlias = (
    "Callable[[Query], Awaitable[Iterable[tuple[str, str]]]]"
)
ChoiceItems: TypeAlias = "list[tuple[str, str]]"
PagingItemsFn: TypeAlias = (
    "Callable[[Query, int, int], Awaitable[tuple[Iterable[tuple[str, str]], bool]]]"  # noqa: E501
)
