from __future__ import annotations

__all__ = (
    "AbstractRowBuilder",
    "Choice",
    "Paging",
    "Row",
)

import asyncio
from abc import ABC
from abc import abstractmethod
from itertools import islice
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import cast

from yatbaf.handler import Handler
from yatbaf.types import InlineKeyboardButton

from .filter import CallbackPayload

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Iterator

    from yatbaf.router import OnCallbackQuery
    from yatbaf.types import CallbackQuery
    from yatbaf.typing import HandlerCallable

    from .button import AbstractButton
    from .menu import Menu
    from .payload import Payload
    from .typing import ChoiceItems
    from .typing import ChoiceItemsFn
    from .typing import PagingItemsFn
    from .typing import Query


class AbstractRowBuilder(ABC):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"

    @abstractmethod
    def _init(
        self,
        menu: Menu,
        router: OnCallbackQuery,
        payload: Payload,
    ) -> None:
        pass

    @abstractmethod
    async def _build(self, q: Query) -> list[list[InlineKeyboardButton]]:
        pass


class Row(AbstractRowBuilder):
    __slots__ = ("_buttons",)

    def __init__(self, buttons: list[AbstractButton]) -> None:
        self._buttons = buttons

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Row)
            and (other is self or (other._buttons == self._buttons))
        )

    def _init(
        self,
        menu: Menu,
        router: OnCallbackQuery,
        payload: Payload,
    ) -> None:
        for button in self._buttons:
            button._init(menu, router, payload)

    async def _build(self, q: Query) -> list[list[InlineKeyboardButton]]:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(b._build(q)) for b in self._buttons]
        if row := [b for t in tasks if (b := t.result()) is not None]:
            return [row]
        return row  # type: ignore[return-value]


T = TypeVar("T")


def batched(iterable: Iterable[T], n: int) -> Iterator[tuple[T, ...]]:
    """:meta private:"""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def build_rows(
    items: Iterable[tuple[str, str]],
    payload: str,
    per_row: int,
) -> list[list[InlineKeyboardButton]]:
    """:meta private:"""
    return [  # yapf: disable
        [
            InlineKeyboardButton(
                text=title,
                callback_data=f"{payload}{extra}",
            )
            for title, extra in row
        ]
        for row in batched(items, per_row)
    ]


class Choice(AbstractRowBuilder):
    """Choice row builder."""

    __slots__ = (
        "_action",
        "_items",
        "_items_per_row",
        "_payload",
        "_submenu",
    )

    def __init__(
        self,
        items: ChoiceItems | ChoiceItemsFn | Iterable[str | int],
        action: HandlerCallable[CallbackQuery] | None = None,
        submenu: str | None = None,
        items_per_row: int = 1,
    ) -> None:
        """
        :param items: Callable or list of items.
        :param action: *Optional.* CallbackQuery handler.
        :param submenu: *Optional.* Submenu name.
        :param items_per_row: *Optional.* Number of items on each row; 1-8.

        .. note::

            Use ``submenu`` to open submenu with button payload; use ``action``
            to execute callback with button payload.
        """
        if ((action is None and submenu is None)
                or (action is not None and submenu is not None)):
            raise ValueError("you must use `submenu` OR `action`")

        self._items_per_row = max(min(items_per_row, 8), 1)
        self._items: ChoiceItems | ChoiceItemsFn = (  # yapf: disable
            items
            if callable(items)
            else [
                (str(i), str(i)) if isinstance(i, str | int) else i
                for i in items
            ]
        )
        self._submenu = submenu
        self._action = action
        self._payload: str | None = None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Choice) and (  # yapf: disable
            other is self or (
                other._action is self._action
                and other._items == self._items
            )
        )

    def _init(
        self,
        menu: Menu,
        router: OnCallbackQuery,
        payload: Payload,
    ) -> None:
        if self._payload is not None:
            raise ValueError(f"{self!r} must be unique.")

        if self._submenu is not None:
            self._payload = f"{menu.get_submenu(self._submenu)._prefix}##"
            return

        self._payload = payload.get()
        handler = Handler(
            cast("HandlerCallable[CallbackQuery]", self._action),
            update_type=router._update_type,
            filters=[CallbackPayload(self._payload)],
        )

        if handler in router._handlers:
            raise ValueError(f"{self!r} `action` must be unique.")

        router.add_handler(handler)

    async def _build(self, q: Query) -> list[list[InlineKeyboardButton]]:
        return build_rows(
            await it(q) if callable(it := self._items) else it,
            self._payload,  # type: ignore[arg-type]
            self._items_per_row,
        )


class Paging(AbstractRowBuilder):
    """Paging row builder."""

    def __init__(
        self,
        items: PagingItemsFn,
        action: HandlerCallable[CallbackQuery] | None = None,
        submenu: str | None = None,
        items_per_page: int = 5,
        items_per_row: int = 1,
        prev_btn_title: str = "Prev",
        next_btn_title: str = "Next",
    ) -> None:
        """
        :param items: A callable that returns the list of items for current page.
        :param action: *Optional.* CallbackQuery handler.
        :param submenu: *Optional.* Submenu name.
        :param items_per_page: *Optional.* Number of items per page; 1-100.
        :param items_per_row: *Optional.* Number of items per row; 1-8.
        :param prev_btn_title: *Optional.* Title for button 'Previous page'.
        :param next_btn_title: *Optional.* Title for button 'Next page'.

        .. note::

            Use ``submenu`` to open submenu with button payload; use ``action``
            to execute callback with button payload.
        """  # noqa: E501
        self._items = items
        self._items_per_page = max(min(items_per_page, 100), 1)
        self._items_per_row = max(min(items_per_row, 8), 1)
        self._payload: str | None = None
        self._nav_payload: str | None = None
        self._prev_btn_title = prev_btn_title
        self._next_btn_title = next_btn_title
        if ((action is None and submenu is None)
                or (action is not None and submenu is not None)):
            raise ValueError("you must use `submenu` OR `action`")
        self._submenu = submenu
        self._action = action

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Paging) and (  # yapf: disable
            other is self or (
                other._action is self._action
                and other._items is self._items
                and other._items_per_row == self._items_per_row
                and other._items_per_page == self._items_per_page
            )
        )

    def _init(
        self,
        menu: Menu,
        router: OnCallbackQuery,
        payload: Payload,
    ) -> None:
        if self._payload is not None:
            raise ValueError(f"{self!r} must be unique.")

        if self._submenu is not None:
            self._payload = f"{menu.get_submenu(self._submenu)._prefix}##"

        else:
            self._payload = payload.get()
            handler = Handler(
                cast("HandlerCallable[CallbackQuery]", self._action),
                filters=[CallbackPayload(self._payload)],
                update_type=router._update_type,
            )
            if handler in router._handlers:
                raise ValueError(f"{self!r} `action` must be unique.")
            router.add_handler(handler)

        self._nav_payload = f"{menu._prefix}##"

    @staticmethod
    def _parse_offset(payload: str) -> int:
        offset = 0
        if offset_list := payload.rsplit("#", maxsplit=1)[1:]:
            try:
                offset = int(offset_list[0])
            except ValueError:
                pass
        return max(0, offset)

    async def _build(self, q: Query) -> list[list[InlineKeyboardButton]]:
        offset = self._parse_offset(getattr(q, "data", ""))
        items, is_last = await self._items(q, offset, self._items_per_page)
        markup = build_rows(
            items,
            self._payload,  # type: ignore[arg-type]
            self._items_per_row,
        )
        nav = []
        # add button `Previous page`
        if offset > 0:
            extra = offset - self._items_per_page
            nav.append(
                InlineKeyboardButton(
                    text=self._prev_btn_title,
                    callback_data=f"{self._nav_payload}#{extra}",
                )
            )
        # add button `Next page`
        if not is_last:
            extra = offset + self._items_per_page
            nav.append(
                InlineKeyboardButton(
                    text=self._next_btn_title,
                    callback_data=f"{self._nav_payload}#{extra}",
                )
            )
        if nav:
            markup.append(nav)
        return markup
