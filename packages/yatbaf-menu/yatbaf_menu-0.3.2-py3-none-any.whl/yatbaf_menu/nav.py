from __future__ import annotations

__all__ = ("MenuNav",)

from typing import TYPE_CHECKING
from typing import cast

from yatbaf.exceptions import MethodInvokeError

if TYPE_CHECKING:
    from yatbaf.types import CallbackQuery
    from yatbaf.types import Message

    from .menu import Menu


class MenuNav:
    """Menu navigation.

    Usage::

        async def button_action(q: CallbackQuery) -> None:
            nav = q.ctx["menu"]
            ...

    .. important::

        Make sure the ``q.message`` is :class:`~yatbaf.types.Message` before
        use these methods.

    """

    __slots__ = (
        "_query",
        "_menu",
    )

    def __init__(self, menu: Menu, query: CallbackQuery, /) -> None:
        """
        :param menu: Current menu.
        :param query: Current query.
        """
        self._query = query
        self._menu = menu

    @property
    def menu(self) -> Menu:
        """Current :class:`~yatbaf_menu.menu.Menu` instance."""
        return self._menu

    async def _open_menu(self, menu: Menu) -> None:
        message = cast("Message", self._query.message)
        params = await menu.get_message_params(self._query)
        await message.edit(**params)

    async def goto(self, path: str) -> None:
        """Use this method to go to menu by path.

        :param path: Path to menu relative to main menu. Separated by dots.
        """
        menu = self._menu.get_menu(path)
        await self._open_menu(menu)

    async def open_previous(self) -> None:
        """Use this method to go to previous menu."""
        menu = self._menu._parent
        if menu is None:
            return
        await self._open_menu(menu)

    async def open_main(self) -> None:
        """Use this method to go to main menu."""
        menu = self._menu.get_root()
        await self._open_menu(menu)

    async def open_submenu(self, name: str) -> None:
        """Use this method to go to submenu.

        :param name: Submenu name.
        """
        menu = self._menu.get_submenu(name)
        await self._open_menu(menu)

    async def open(self) -> None:
        await self._open_menu(self._menu)

    async def refresh(self) -> None:
        """Use this method to refresh current menu."""
        await self._open_menu(self._menu)

    async def close(self) -> None:
        """Use this method to close the menu."""
        message = cast("Message", self._query.message)
        try:
            await message.delete()
        except MethodInvokeError:
            await message.edit_reply_markup()
