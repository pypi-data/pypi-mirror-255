import pytest

from yatbaf import OnCallbackQuery
from yatbaf.exceptions import SkipRouterException
from yatbaf_menu.button import URL
from yatbaf_menu.menu import Menu
from yatbaf_menu.middleware import CutPayloadMiddileware
from yatbaf_menu.middleware import InjectMenuMiddleware
from yatbaf_menu.utils import _build_base_router
from yatbaf_menu.utils import _build_fallback_router
from yatbaf_menu.utils import _build_menu_router
from yatbaf_menu.utils import _build_root_router


@pytest.fixture
def menu(prefix):
    result = Menu(
        title="menu title",
        name="test_menu",
        buttons=[URL(title="button", url="example.com")],
    )
    result._prefix = prefix
    return result


@pytest.mark.asyncio
async def test_build_menu_router(menu):
    router = _build_menu_router(menu)

    assert router._middleware[0].obj is InjectMenuMiddleware
    assert router._middleware[0].is_local
    assert router._middleware[0].is_handler
    assert router._handlers[0]._filters[0].payload == f"{menu._prefix}##"


@pytest.mark.asyncio
async def test_build_base_router(menu, callback_query):
    version = "00"
    router = _build_base_router(menu, version)

    assert not router._handlers
    assert router._middleware[0].obj is CutPayloadMiddileware
    assert router._middleware[0].is_handler
    assert router._guards
    guard = router._guards[0]

    callback_query.data = f"{menu._prefix[:2]}{version}ee"
    guard(callback_query)

    callback_query.data = f"{menu._prefix[:2]}01ee"
    with pytest.raises(SkipRouterException) as err:
        guard(callback_query)
    assert err.value.skip_nested


def test_build_fallback_router(menu):
    router = _build_fallback_router(menu, "updated")

    assert not router._guards
    assert router._middleware
    assert router._middleware[0].obj is InjectMenuMiddleware
    assert router._middleware[0].is_handler
    assert router._middleware[0].is_local
    assert router._middleware[0].params["menu"] is menu


@pytest.mark.asyncio
async def test_build_root_router(menu, callback_query):
    base = OnCallbackQuery(handlers=[object()])
    fallback = OnCallbackQuery(handlers=[object()])

    router = _build_root_router(
        menu=menu,
        base_router=base,
        fallback_router=fallback,
    )

    assert router._routers
    assert router._routers[0] is base
    assert router._routers[1] is fallback

    assert not router._middleware
    assert router._guards
    guard = router._guards[0]

    callback_query.data = f"{menu._prefix}qwer123"
    guard(callback_query)

    callback_query.data = "any"
    with pytest.raises(SkipRouterException) as err:
        guard(callback_query)
    assert err.value.skip_nested

    callback_query.data = None
    with pytest.raises(SkipRouterException) as err:
        guard(callback_query)
    assert err.value.skip_nested
