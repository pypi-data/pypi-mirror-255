import pytest

from yatbaf.types import InlineKeyboardButton
from yatbaf_menu.menu import Menu
from yatbaf_menu.row import Choice

PAYLOAD = "~a00a"


def test_no_action_and_submenu():
    with pytest.raises(ValueError):
        Choice(items=[1, 2, 3])


def test_action_and_submenu():
    with pytest.raises(ValueError):
        Choice(
            action=object(),
            submenu="menu",
            items=[1, 2, 3],
        )


def test_init_submenu(prefix, router, payload):
    menu = Menu(
        title="menu",
        name="menu",
        submenu=[
            submenu := Menu(
                title="submenu",
                name="submenu",
                back_btn_title="back",
            ),
        ],
        buttons=[
            choice := Choice(
                submenu="submenu",
                items=[1, 2, 3],
            ),
        ],
    )
    menu._prefix = prefix
    submenu._prefix = f"{prefix[:-2]}bb"
    choice._init(menu, router, payload)
    assert choice._payload == f"{submenu._prefix}##"
    assert not router._handlers


def test_init_action(prefix, router, payload):
    action = object()
    menu = Menu(
        title="menu",
        name="menu",
        buttons=[
            choice := Choice(
                action=action,
                items=[("1", "1"), ("2", "2")],
                items_per_row=1,
            )
        ],
    )
    menu._prefix = prefix
    choice._init(menu, router, payload)
    assert choice._payload is not None
    assert router._handlers[0]._fn is action
    assert router._handlers[0]._filters[0].payload == choice._payload


def test_init_duplicate(prefix, router, payload):
    action = object()
    menu = Menu(
        title="menu",
        name="menu",
        buttons=[
            choice := Choice(
                action=action,
                items=[("1", "1"), ("2", "2")],
                items_per_row=1,
            ),
        ]
    )
    menu._prefix = prefix
    choice._payload = "qwe"
    with pytest.raises(ValueError):
        choice._init(menu, router, payload)


def test_init_duplicate_action(prefix, router, payload):
    action = object()
    menu = Menu(
        title="menu",
        name="menu",
        buttons=[
            choice := Choice(
                action=action,
                items=[("1", "1"), ("2", "2")],
            )
        ]
    )
    menu._prefix = prefix
    router.add_handler(action)
    with pytest.raises(ValueError):
        choice._init(menu, router, payload)


@pytest.mark.asyncio
async def test_build():

    async def _items(_):
        return [("1", "1"), ("2", "2"), ("3", "3")]

    choice = Choice(action=object(), items=_items, items_per_row=1)
    choice._payload = PAYLOAD
    assert choice._items is _items

    result = await choice._build(None)
    assert result == [
        [InlineKeyboardButton(text="1", callback_data=f"{PAYLOAD}1")],
        [InlineKeyboardButton(text="2", callback_data=f"{PAYLOAD}2")],
        [InlineKeyboardButton(text="3", callback_data=f"{PAYLOAD}3")],
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "ipr,expected",
    [
        (
            1,
            [
                [InlineKeyboardButton(text="1", callback_data=f"{PAYLOAD}1")],
                [InlineKeyboardButton(text="2", callback_data=f"{PAYLOAD}2")],
                [InlineKeyboardButton(text="3", callback_data=f"{PAYLOAD}3")],
            ]
        ),
        (
            3,
            [
                [
                    InlineKeyboardButton(text="1", callback_data=f"{PAYLOAD}1"),
                    InlineKeyboardButton(text="2", callback_data=f"{PAYLOAD}2"),
                    InlineKeyboardButton(text="3", callback_data=f"{PAYLOAD}3")
                ],
            ]
        ),
    ]
)
async def test_items_per_row(ipr, expected):
    choice = Choice(action=object(), items=[1, 2, 3], items_per_row=ipr)
    choice._payload = PAYLOAD
    assert choice._items == [("1", "1"), ("2", "2"), ("3", "3")]

    result = await choice._build(None)
    assert result == expected
