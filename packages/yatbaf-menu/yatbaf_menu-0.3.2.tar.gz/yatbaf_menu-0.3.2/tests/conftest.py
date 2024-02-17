import pytest

from yatbaf.router import OnCallbackQuery
from yatbaf.types import CallbackQuery
from yatbaf.types import User
from yatbaf_menu.payload import Payload


@pytest.fixture
def router():
    return OnCallbackQuery()


@pytest.fixture
def prefix():
    return "aa00aa"


@pytest.fixture
def payload(prefix):
    return Payload(prefix)


@pytest.fixture
def user():
    return User(
        id=12345,
        is_bot=False,
        first_name="Test",
    )


@pytest.fixture
def callback_query(user):
    return CallbackQuery(
        id=12345,
        chat_instance="test",
        from_=user,
    )
