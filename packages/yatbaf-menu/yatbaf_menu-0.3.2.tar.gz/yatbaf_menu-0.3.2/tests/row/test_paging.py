import pytest

from yatbaf.types import InlineKeyboardButton
from yatbaf_menu.menu import Menu
from yatbaf_menu.row import Paging

PAYLOAD = "~a00a"
NAV_PAYLOAD = "~a00a"
NEXT_BTN_TITLE = "next"
PREV_BTN_TITLE = "next"


def test_no_action_and_submenu():
    with pytest.raises(ValueError):
        Paging(items=object())


def test_action_and_submenu():
    with pytest.raises(ValueError):
        Paging(action=object(), submenu="menu", items=object())


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
            paging := Paging(
                submenu="submenu",
                items=object(),
            ),
        ],
    )
    menu._prefix = prefix
    submenu._prefix = f"{prefix[:-2]}bb"
    paging._init(menu, router, payload)
    assert paging._payload == f"{submenu._prefix}##"
    assert paging._nav_payload == f"{menu._prefix}##"
    assert len(router._handlers) == 0


def test_init_action(router, payload, prefix):
    action = object()
    menu = Menu(
        title="menu",
        name="menu",
        buttons=[
            paging := Paging(action=action, items=object()),
        ],
    )
    menu._prefix = prefix
    paging._init(menu, router, payload)
    assert paging._payload is not None
    assert paging._nav_payload == f"{menu._prefix}##"
    assert len(router._handlers) == 1
    assert router._handlers[0]._fn is action


def test_init_duplicate(router, payload, prefix):
    menu = Menu(
        title="menu",
        name="menu",
        buttons=[
            paging := Paging(action=object(), items=object()),
        ],
    )
    menu._prefix = prefix
    paging._payload = "qwe"
    with pytest.raises(ValueError):
        paging._init(menu, router, payload)


def test_init_duplicate_action(router, payload, prefix):
    action = object()
    menu = Menu(
        title="menu",
        name="menu",
        buttons=[
            paging := Paging(action=action, items=object()),
        ],
    )
    menu._prefix = prefix
    router.add_handler(action)
    with pytest.raises(ValueError):
        paging._init(menu, router, payload)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "offset,last_page,expected",
    [  # yapf: disable
        (
            0, False,
            [
                [InlineKeyboardButton(text="1", callback_data=f"{PAYLOAD}1")],
                [InlineKeyboardButton(text="2", callback_data=f"{PAYLOAD}2")],
                [InlineKeyboardButton(text=f"{NEXT_BTN_TITLE}", callback_data=f"{NAV_PAYLOAD}#2")],  # noqa: E501
            ],
        ),
        (
            2, False,
            [
                [InlineKeyboardButton(text="1", callback_data=f"{PAYLOAD}1")],
                [InlineKeyboardButton(text="2", callback_data=f"{PAYLOAD}2")],
                [
                    InlineKeyboardButton(text=f"{PREV_BTN_TITLE}", callback_data=f"{NAV_PAYLOAD}#0"),  # noqa: E501
                    InlineKeyboardButton(text=f"{NEXT_BTN_TITLE}", callback_data=f"{NAV_PAYLOAD}#4"),  # noqa: E501
                ],
            ],
        ),
        (
            2, True,
            [
                [InlineKeyboardButton(text="1", callback_data=f"{PAYLOAD}1")],
                [InlineKeyboardButton(text="2", callback_data=f"{PAYLOAD}2")],
                [InlineKeyboardButton(text=f"{PREV_BTN_TITLE}", callback_data=f"{NAV_PAYLOAD}#0")],  # noqa: E501
            ],
        ),
    ]
)
async def test_build(callback_query, offset, last_page, expected):

    async def _items(q, o, i):  # noqa: U100
        return ([("1", "1"), ("2", "2")], last_page)

    paging = Paging(
        action=object(),
        items=_items,
        items_per_row=1,
        items_per_page=2,
        prev_btn_title=PREV_BTN_TITLE,
        next_btn_title=NEXT_BTN_TITLE,
    )
    paging._payload = PAYLOAD
    paging._nav_payload = NAV_PAYLOAD
    callback_query.data = f"#{offset}"
    result = await paging._build(callback_query)
    assert result == expected


@pytest.mark.parametrize(
    "payload,expected",
    [
        ("12", 0),
        ("", 0),
        ("#12", 12),
        ("#-12", 0),
        ("payload#12", 12),
        ("data#payload#12", 12),
    ]
)
def test_parse_offset(payload, expected):
    assert Paging._parse_offset(payload) == expected
