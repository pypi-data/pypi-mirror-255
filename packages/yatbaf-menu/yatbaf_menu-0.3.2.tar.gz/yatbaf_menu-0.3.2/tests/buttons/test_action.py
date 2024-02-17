import pytest

from yatbaf.types import InlineKeyboardButton
from yatbaf_menu import Action


def test_init(router, menu, payload):
    action = object()
    button = Action(title="button", action=action)
    button._init(menu, router, payload)
    assert button._payload is not None
    assert router._handlers[0]._fn is action


def test_init_duplicate(router, menu, payload):
    action = object()
    button = Action(title="button", action=action)
    button._payload = "aa00aa"
    with pytest.raises(ValueError):
        button._init(menu, router, payload)


def test_init_duplicate_action(router, menu, payload):
    action = object()
    button1 = Action(title="button1", action=action)
    button1._init(menu, router, payload)
    button2 = Action(title="button2", action=action)
    with pytest.raises(ValueError):
        button2._init(menu, router, payload)


@pytest.mark.asyncio
async def test_build(callback_query):
    paylaod = "aa00aa"
    button = Action(title="button", action=object())
    button._payload = paylaod

    result = await button._build(callback_query)
    assert result == InlineKeyboardButton(text="button", callback_data=paylaod)


@pytest.mark.asyncio
async def test_build_not_visible(callback_query):

    async def _visible(_):
        return False

    paylaod = "aa00aa"
    button = Action(title="button", action=object(), show=_visible)
    button._payload = paylaod

    result = await button._build(callback_query)
    assert result is None


@pytest.mark.asyncio
async def test_build_extra_payload(callback_query):
    paylaod = "aa00aa"
    extra = "some-payload"

    def _payload(_):
        return extra

    button = Action(title="button", action=object(), payload=_payload)
    button._payload = paylaod

    result = await button._build(callback_query)
    assert result == InlineKeyboardButton(
        text="button",
        callback_data=f"{paylaod}{extra}",
    )
