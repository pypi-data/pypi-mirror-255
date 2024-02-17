from __future__ import annotations

__all__ = (
    "AbstractButton",
    "Action",
    "URL",
    "Submenu",
    "Back",
)

import asyncio
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from yatbaf.handler import Handler
from yatbaf.types import InlineKeyboardButton

from .filter import CallbackPayload

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable

    from yatbaf import OnCallbackQuery

    from .menu import Menu
    from .payload import Payload
    from .typing import Query


class AbstractButton(ABC):
    __slots__ = ()

    @abstractmethod
    def _init(
        self, menu: Menu, router: OnCallbackQuery, payload: Payload, /
    ) -> None:
        pass

    @abstractmethod
    async def _build(self, q: Query, /) -> InlineKeyboardButton | None:
        pass


class BaseButton(AbstractButton):
    __slots__ = (
        "_title",
        "_show",
    )

    def __init__(
        self,
        *,
        title: str | Callable[[Query], Awaitable[str]],
        show: Callable[[Query], Awaitable[bool]] | None = None,
    ) -> None:
        self._title = title
        self._show = show

    def __repr__(self) -> str:
        title = "`dynamic`" if callable(t := self._title) else t
        return f"<{self.__class__.__name__}[{title=!r}]>"

    async def _get_title(self, q: Query, /) -> str:
        if callable(self._title):
            return await self._title(q)
        return self._title

    async def _is_visible(self, q: Query, /) -> bool:
        if self._show is not None:
            return await self._show(q)
        return True


class CallbackButton(BaseButton):
    __slots__ = (
        "_payload",
        "_payload_extra",
    )

    def __init__(
        self,
        title: str | Callable[[Query], Awaitable[str]],
        show: Callable[[Query], Awaitable[bool]] | None = None,
        payload: Callable[[Query], str] | None = None,
    ) -> None:
        super().__init__(
            title=title,
            show=show,
        )
        self._payload: str | None = None
        self._payload_extra = payload

    def __eq__(self, other: object) -> bool:
        return other is self or (  # yapf: disable
            isinstance(other, self.__class__) and (
                other._title == self._title
                and other._show == self._show
                and other._payload_extra == self._payload_extra
            )
        )

    async def _build(self, q: Query) -> InlineKeyboardButton | None:
        if not await self._is_visible(q):
            return None

        extra = "" if (f := self._payload_extra) is None else f(q)
        return InlineKeyboardButton(
            text=await self._get_title(q),
            callback_data=f"{self._payload}{extra}",
        )


class Action(CallbackButton):
    """This button does the action"""
    __slots__ = ("_action",)

    def __init__(
        self,
        title: str | Callable[[Query], Awaitable[str]],
        action: Callable[[Query], Awaitable[None]],
        *,
        show: Callable[[Query], Awaitable[bool]] | None = None,
        payload: Callable[[Query], str] | None = None,
    ) -> None:
        """
        :param title: String or Callable which returns button title.
        :param action: Callable to run on click. Must be unique for the menu.
        :param show: *Optional.* Callable which returns visibility status.
        :param payload: *Optional.* Sync function, returned string will be used
            as `callback_data`.
        """
        super().__init__(
            title=title,
            show=show,
            payload=payload,
        )
        self._action = action

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and other._action == self._action  # type: ignore[attr-defined]
        )

    def _init(
        self, m: Menu, router: OnCallbackQuery, payload: Payload, /
    ) -> None:
        if self._payload is not None:
            raise ValueError(
                f"{self!r} button must be unique to the entire menu."
            )

        self._payload = payload.get()
        handler = Handler(
            self._action,
            update_type=router._update_type,
            filters=[CallbackPayload(self._payload)],
        )
        if handler in router._handlers:
            raise ValueError(f"{self!r} `action` must be unique to menu.")

        router.add_handler(handler)


class URL(BaseButton):
    """This button will open URL"""
    __slots__ = ("_url",)

    def __init__(
        self,
        title: str | Callable[[Query], Awaitable[str]],
        url: str | Callable[[Query], Awaitable[str]],
        *,
        show: Callable[[Query], Awaitable[bool]] | None = None,
    ) -> None:
        """
        :param url: String or Callable which returns url.
        :param title: String or Callable which returns button title.
        :param show: *Optional.* Callable which returns visibility status.
        """
        super().__init__(
            title=title,
            show=show,
        )
        self._url = url

    def __eq__(self, other: object) -> bool:
        return isinstance(other, URL) and (  # yapf: disable
            other is self or (
                other._title == self._title
                and other._url == self._url
                and other._show == self._show
            )
        )

    def _init(self, m: Menu, r: OnCallbackQuery, p: Payload, /) -> None:
        pass  # nothing to do

    async def _get_url(self, q: Query, /) -> str:
        if callable(self._url):
            return await self._url(q)
        return self._url

    async def _build(self, q: Query, /) -> InlineKeyboardButton | None:
        if not await self._is_visible(q):
            return None

        async with asyncio.TaskGroup() as tg:
            title = tg.create_task(self._get_title(q))
            url = tg.create_task(self._get_url(q))

        return InlineKeyboardButton(
            text=title.result(),
            url=url.result(),
        )


class Submenu(CallbackButton):
    """This button will open next menu"""
    __slots__ = ("_menu",)

    def __init__(
        self,
        title: str | Callable[[Query], Awaitable[str]],
        menu: str,
        *,
        show: Callable[[Query], Awaitable[bool]] | None = None,
        payload: Callable[[Query], str] | None = None,
    ) -> None:
        """
        :param menu: Submenu name (see :class:`~yatbaf_menu.menu.Menu`).
        :param title: String or Callable which returns button title.
        :param show: *Optional.* Callable which returns visibility status.
        :param payload: *Optional.* Sync function, returned string will be used
            as `callback_data`.
        """
        super().__init__(
            title=title,
            show=show,
            payload=payload,
        )
        self._menu = menu

    def __repr__(self) -> str:
        title = "`dynamic`" if callable(t := self._title) else t
        menu = self._menu
        return f"<Submenu[{title=}, {menu=}]>"

    def __eq__(self, other: object) -> bool:
        return (
            super().__eq__(other)
            and other._menu == self._menu  # type: ignore[attr-defined]
        )

    def _init(self, menu: Menu, r: OnCallbackQuery, p: Payload, /) -> None:
        if self._payload is not None:
            raise ValueError(f"{self!r} button must be unique.")
        self._payload = f"{menu.get_submenu(self._menu)._prefix}##"


class Back(CallbackButton):
    """This button will open previous menu"""
    __slots__ = ()

    def __init__(
        self,
        title: str | Callable[[Query], Awaitable[str]],
        *,
        payload: Callable[[Query], str] | None = None,
    ) -> None:
        """
        :param title: String or Callable which returns button title.
        :param payload: *Optional.* Sync function, returned string will be used
            as `callback_data`.
        """
        super().__init__(
            title=title,
            payload=payload,
        )

    def _init(self, menu: Menu, r: OnCallbackQuery, p: Payload, /) -> None:
        if self._payload is not None:
            raise ValueError(f"{self!r} button must be unique.")

        if menu._parent is None:
            raise ValueError(f"It is not possible to use {self!r} in {menu!r}.")

        self._payload = f"{menu._parent._prefix}##"
