from __future__ import annotations

__all__ = ("build_router",)

from typing import TYPE_CHECKING
from typing import cast

from yatbaf import OnCallbackQuery
from yatbaf.exceptions import SkipRouterException
from yatbaf.middleware import Middleware

from .filter import CallbackPayload
from .middleware import CutPayloadMiddileware
from .middleware import InjectMenuMiddleware
from .payload import Payload

if TYPE_CHECKING:
    from yatbaf.types import CallbackQuery

    from .menu import Menu
    from .nav import MenuNav

_root_payload_bucket = Payload()


def _build_menu_router(menu: Menu) -> OnCallbackQuery:
    """
    :meta private:

    :param menu: Menu object.
    """
    menu._prefix = cast("str", menu._prefix)
    payload = menu._prefix[3:5]

    def _guard(q: CallbackQuery) -> None:
        if q.data[3:5] == payload:  # type: ignore[index]
            return
        raise SkipRouterException

    menu._guards.insert(0, _guard)
    router = OnCallbackQuery(
        name=menu.name,
        guards=menu._guards,
        middleware=menu._middleware,
    )

    @router(filters=[CallbackPayload(f"{menu._prefix}##")])
    async def _open_menu(q: CallbackQuery) -> None:
        menu: MenuNav = q.ctx["menu"]
        await q.answer()
        await menu.refresh()

    return router


def _build_base_router(menu: Menu, version: str) -> OnCallbackQuery:
    """
    :meta private:

    :param menu: Main menu object.
    """
    router = OnCallbackQuery(
        name=f"{menu.name}-root",
        middleware=[CutPayloadMiddileware],
    )

    @router.guard
    def _guard(q: CallbackQuery) -> None:
        if q.data[2:4] == version:  # type: ignore[index]
            return
        raise SkipRouterException(skip_nested=True)

    return router


def _build_fallback_router(menu: Menu, update_message: str) -> OnCallbackQuery:
    """
    :meta private:

    :param menu: Main menu object.
    :param update_message: Will be shown to the user.
    """
    router = OnCallbackQuery(
        name=f"{menu.name}-fallback",
        middleware=[
            Middleware(
                InjectMenuMiddleware,  # type: ignore[arg-type]
                is_local=True,
                is_handler=True,
                menu=menu,
            ),
        ],
    )

    @router
    async def _fallback(q: CallbackQuery) -> None:
        menu: MenuNav = q.ctx["menu"]
        q.data = None
        await q.answer(text=update_message)
        await menu.open_main()

    return router


def _build_root_router(
    menu: Menu,
    base_router: OnCallbackQuery,
    fallback_router: OnCallbackQuery,
) -> OnCallbackQuery:
    """:meta private:"""
    menu._prefix = cast("str", menu._prefix)
    prefix = menu._prefix[:2]  # root prefix 2 chars

    router = OnCallbackQuery(
        name=f"{menu.name}-base",
        routers=[
            base_router,
            fallback_router,
        ],
    )

    @router.guard
    def _guard(q: CallbackQuery) -> None:
        if (data := q.data) is not None and data[:2] == prefix:
            return
        raise SkipRouterException(skip_nested=True)

    return router


def _init_buttons(menu: Menu, router: OnCallbackQuery) -> None:
    menu._prefix = cast("str", menu._prefix)
    payload = Payload(menu._prefix)
    for row in menu._rows:
        row._init(menu, router, payload)


def _parse_version(version: str | int) -> str:
    version = str(version)
    if len(version) > 2:
        raise ValueError(f"{version=} cannot be longer than 2 characters.")
    return version.zfill(2)


def build_router(
    menu: Menu,
    *,
    version: str | int = 0,
    update_message: str = "This menu was updated.",
) -> OnCallbackQuery:
    """Build menu router.

    :param menu: :class:`~yatbaf_menu.menu.Menu` object.
    :param version: *Optional.* Menu version. Up to 2 chars.
    :param update_message: *Optional.* Will be shown to the user when
        ``version`` is increased.
    :returns: Configured :class:`~yatbaf.router.OnCallbackQuery` object.
    """
    version = _parse_version(version)
    menu_payload = Payload(_root_payload_bucket.get() + version)
    base_router = _build_base_router(menu, version)

    def _init_menu(menu: Menu, base: OnCallbackQuery) -> None:
        menu._prefix = menu_payload.get()
        router = _build_menu_router(menu)
        base.add_router(router)
        for submenu in menu._submenu.values():
            submenu._parent = menu
            _init_menu(submenu, router)
        _init_buttons(menu, router)

    _init_menu(menu, base_router)

    return _build_root_router(
        menu=menu,
        base_router=base_router,
        fallback_router=_build_fallback_router(
            menu=menu,
            update_message=update_message,
        ),
    )
