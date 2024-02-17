import pytest

from yatbaf_menu.menu import Menu


@pytest.fixture
def menu(prefix):
    menu_ = Menu(
        title="menu",
        name="menu",
        back_btn_title="back",
    )
    menu_._prefix = prefix
    return menu_
