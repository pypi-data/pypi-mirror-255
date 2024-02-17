import pytest

from yatbaf.types import InlineKeyboardButton
from yatbaf_menu.button import URL


@pytest.mark.asyncio
async def test_build(callback_query):
    button = URL(title="link", url="url")
    result = await button._build(callback_query)
    assert result == InlineKeyboardButton(text="link", url="url")


@pytest.mark.asyncio
async def test_build_dynamic_url(callback_query):

    async def _url(_):
        return "dyn_url"

    button = URL(title="link", url=_url)
    result = await button._build(callback_query)
    assert result == InlineKeyboardButton(text="link", url="dyn_url")
