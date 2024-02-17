import pytest

from yatbaf.types import InlineKeyboardButton
from yatbaf.types import InlineKeyboardMarkup
from yatbaf_menu.button import URL
from yatbaf_menu.menu import Menu


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "buttons,markup",
    [
        [
            [
                URL(url="example.com", title="example 1"),
                URL(url="example.com", title="example 2"),
                URL(url="example.com", title="example 3"),
                URL(url="example.com", title="example 4"),
            ],
            [
                [InlineKeyboardButton(url="example.com", text="example 1")],
                [InlineKeyboardButton(url="example.com", text="example 2")],
                [InlineKeyboardButton(url="example.com", text="example 3")],
                [InlineKeyboardButton(url="example.com", text="example 4")],
            ],
        ],
        [
            [
                [
                    URL(url="example.com", title="example 1"),
                    URL(url="example.com", title="example 2"),
                    URL(url="example.com", title="example 3"),
                ],
                URL(url="example.com", title="example 4"),
            ],
            [
                [
                    InlineKeyboardButton(url="example.com", text="example 1"),
                    InlineKeyboardButton(url="example.com", text="example 2"),
                    InlineKeyboardButton(url="example.com", text="example 3"),
                ],
                [InlineKeyboardButton(url="example.com", text="example 4")],
            ],
        ],
        [
            [
                [
                    URL(url="example.com", title="example 1"),
                    URL(url="example.com", title="example 2"),
                ],
                [
                    URL(url="example.com", title="example 3"),
                    URL(url="example.com", title="example 4"),
                ],
            ],
            [
                [
                    InlineKeyboardButton(url="example.com", text="example 1"),
                    InlineKeyboardButton(url="example.com", text="example 2")
                ],
                [
                    InlineKeyboardButton(url="example.com", text="example 3"),
                    InlineKeyboardButton(url="example.com", text="example 4")
                ],
            ],
        ],
    ]
)
async def test_build_markup(buttons, markup):
    menu = Menu(title="test", name="test", buttons=buttons)
    assert await menu._get_markup(None) == InlineKeyboardMarkup(markup)
