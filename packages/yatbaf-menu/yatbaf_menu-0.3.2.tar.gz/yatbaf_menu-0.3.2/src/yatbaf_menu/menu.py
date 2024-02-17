from __future__ import annotations

__all__ = ("Menu",)

import asyncio
from itertools import count
from typing import TYPE_CHECKING
from typing import Any
from typing import cast
from typing import final

from yatbaf.middleware import Middleware
from yatbaf.types import InlineKeyboardMarkup

from .button import Back
from .middleware import InjectMenuMiddleware
from .row import AbstractRowBuilder
from .row import Row

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable
    from collections.abc import Sequence

    from yatbaf.enums import ParseMode
    from yatbaf.router import InitMiddlewareType
    from yatbaf.types import CallbackQuery
    from yatbaf.typing import GuardCallable

    from .button import AbstractButton
    from .typing import Query

_menu_count = count(1).__next__


def _parse_markup(
    markup: list[AbstractButton | AbstractRowBuilder | list[AbstractButton]]
) -> list[AbstractRowBuilder]:
    result: list[AbstractRowBuilder] = []
    for row in markup:
        if isinstance(row, list):
            for obj in row:
                if issubclass(type(obj), AbstractRowBuilder):
                    if len(row) != 1:
                        raise ValueError(
                            f"It is not possible to use {obj!r} with "
                            "other objects in the same row"
                        )
                    result.append(cast("AbstractRowBuilder", obj))
                    break
            else:
                result.append(Row(row))

        # row builder
        elif issubclass(type(row), AbstractRowBuilder):
            result.append(cast("AbstractRowBuilder", row))

        # single button
        else:
            result.append(Row([cast("AbstractButton", row)]))

    return result


def _parse_menu_name(name: str | None) -> str:
    if name is not None:
        return name.lower()
    return f"menu{_menu_count()}"


@final
class Menu:
    """Menu object."""

    __slots__ = (
        "_title",
        "_name",
        "_buttons",
        "_submenu",
        "_rows",
        "_parent",
        "_prefix",
        "_guards",
        "_middleware",
        "_parse_mode",
    )

    def __init__(  # yapf: disable
        self,
        *,
        title: str | Callable[[Query], Awaitable[str]],
        name: str | None = None,
        buttons: list[AbstractButton | AbstractRowBuilder | list[AbstractButton]] | None = None,  # noqa: E501
        submenu: Sequence[Menu] | None = None,
        guards: Sequence[GuardCallable[CallbackQuery]] | None = None,
        middleware: Sequence[InitMiddlewareType[CallbackQuery]] | None = None,
        back_btn_title: str | Callable | None = None,
        parse_mode: ParseMode | None = None,
    ) -> None:
        """
        :param title: String or Callable which return menu title.
        :param name: *Optional.* Menu name.
        :param submenu: *Optional.* Sequence of :class:`Menu`.
        :param buttons: *Optional.* A list of buttons.
        :param parse_mode: *Optional.* Parse mode for menu title.
        :param back_btn_title: *Optional.* Pass a title if you want to add
            a 'back button' to this menu. For submenu only.
        :param guards: *Optional.* Sequence of :class:`~yatbaf.typing.Guard`
        :param middleware: *Optional.* Sequence of :class:`~yatbaf.typing.Middleware`
        """  # noqa: E501
        self._name = _parse_menu_name(name)
        self._title = title
        self._prefix: str | None = None

        buttons = buttons if buttons is not None else []
        if back_btn_title is not None:
            buttons.append(Back(title=back_btn_title))
        if not buttons:
            raise ValueError(f"{self!r} must have at least one button.")

        self._rows = _parse_markup(buttons)

        self._submenu = {} if submenu is None else {m.name: m for m in submenu}
        self._parent: Menu | None = None

        self._guards = list(guards) if guards is not None else []
        self._middleware = list(middleware) if middleware is not None else []
        self._middleware.append(
            Middleware(
                InjectMenuMiddleware,  # type: ignore[arg-type]
                is_local=True,
                is_handler=True,
                menu=self,
            )
        )
        self._parse_mode = parse_mode

    def __repr__(self) -> str:
        return f"<Menu[{self._name}]>"

    @property
    def name(self) -> str:
        """Menu name."""
        return self._name

    def get_submenu(self, name: str) -> Menu:
        """Returns submenu with by name.

        :param name: Submenu name.
        :raises ValueError: If submenu with ``name`` is not found.
        """
        try:
            return self._submenu[name]
        except KeyError:
            raise ValueError(f"Menu {name} not found in {self!r}") from None

    def get_root(self) -> Menu:
        """Returns main menu."""
        menu = self
        while menu._parent is not None:
            menu = menu._parent
        return menu

    def get_menu(self, path: str) -> Menu:
        """Returns menu by path.

        :param path: Path to menu.
        :raises ValueError: If ``path`` is not found.
        """
        menu = self.get_root()
        for name in path.split("."):
            menu = menu.get_submenu(name)
        return menu

    async def _get_title(self, q: Query, /) -> str:
        if callable(self._title):
            return await self._title(q)
        return self._title

    async def _get_markup(self, q: Query, /) -> InlineKeyboardMarkup:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(r._build(q)) for r in self._rows]
        return InlineKeyboardMarkup([
            row for task in tasks for row in task.result()
        ])

    async def get_message_params(self, query: Query) -> dict[str, Any]:
        """Create parameters for message.

        Use it to open menu::

            @on_message(filters=[Command("menu")])
            async def open_menu(message: Message) -> None:
                params = await menu.get_message_params(message)
                await message.answer(**params)

        :param query: :class:`~yatbaf.types.message.Message` or
            :class:`~yatbaf.types.callback_query.CallbackQuery` object.
        """
        async with asyncio.TaskGroup() as tg:
            title = tg.create_task(self._get_title(query))
            markup = tg.create_task(self._get_markup(query))

        return {
            "text": title.result(),
            "reply_markup": markup.result(),
            "parse_mode": self._parse_mode,
        }
