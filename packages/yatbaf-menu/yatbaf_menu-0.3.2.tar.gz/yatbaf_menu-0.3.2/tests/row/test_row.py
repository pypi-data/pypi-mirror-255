import pytest

from yatbaf.types import InlineKeyboardButton
from yatbaf_menu.button import URL
from yatbaf_menu.row import Row


@pytest.mark.asyncio
async def test_row():
    row = Row([
        URL(url="example.com", title="example 1"),
        URL(url="example.com", title="example 2"),
    ])

    result = await row._build(None)
    assert result == [
        [
            InlineKeyboardButton(url="example.com", text="example 1"),
            InlineKeyboardButton(url="example.com", text="example 2")
        ],
    ]
