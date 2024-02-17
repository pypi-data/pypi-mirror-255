import pytest

from yatbaf.types import InlineKeyboardButton
from yatbaf_menu import Menu
from yatbaf_menu import Submenu


def test_init_no_submenu(router, payload):
    menu = Menu(
        title="menu",
        name="menu",
        buttons=[
            button := Submenu(title="submenu", menu="submenu"),
        ],
    )
    with pytest.raises(ValueError):
        button._init(menu, router, payload)


def test_init(router, prefix, payload):
    menu = Menu(
        title="menu",
        name="menu",
        buttons=[
            button := Submenu(title="submenu", menu="submenu"),
        ],
        submenu=[
            submenu := Menu(
                title="submenu",
                name="submenu",
                back_btn_title="back",
            ),
        ],
    )
    submenu._prefix = prefix
    button._init(menu, router, payload)
    assert button._payload == f"{submenu._prefix}##"


def test_init_duplicate(router, prefix, payload):
    menu = Menu(
        title="menu",
        name="menu",
        buttons=[
            button := Submenu(title="submenu", menu="submenu"),
        ],
        submenu=[
            Menu(
                title="submenu",
                name="submenu",
                back_btn_title="back",
            ),
        ]
    )
    button._payload = f"{prefix}##"
    with pytest.raises(ValueError):
        button._init(menu, router, payload)


@pytest.mark.asyncio
async def test_build(callback_query, prefix):
    button = Submenu(title="submenu", menu="submenu")
    button._payload = f"{prefix}##"
    result = await button._build(callback_query)
    assert result == InlineKeyboardButton(
        text="submenu",
        callback_data=button._payload,
    )


@pytest.mark.asyncio
async def test_build_not_visible(callback_query, prefix):

    async def _visible(_):
        return False

    button = Submenu(title="submenu", menu="submenu", show=_visible)
    button._payload = f"{prefix}##"
    result = await button._build(callback_query)
    assert result is None
