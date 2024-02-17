from yatbaf_menu.button import Action
from yatbaf_menu.button import Back
from yatbaf_menu.button import Submenu
from yatbaf_menu.menu import Menu
from yatbaf_menu.row import Row
from yatbaf_menu.utils import build_router


async def action1(_):
    pass


async def action2(_):
    pass


def test_build():
    menu = Menu(
        title="title",
        name="main",
        buttons=[
            Submenu(title="sub1", menu="sub1"),
            Action(title="button2", action=action2),
        ],
        submenu=[
            Menu(
                title="title",
                name="sub1",
                buttons=[Submenu(title="sub2", menu="sub2")],
                submenu=[
                    Menu(
                        title="title",
                        name="sub2",
                        back_btn_title="back",
                    ),
                ],
                back_btn_title="back",
            ),
            Menu(
                title="title",
                name="sub3",
                buttons=[Action(title="button1", action=action1)],
                back_btn_title="back",
            )
        ],
    )

    router = build_router(menu)
    """
    root-router
      ├── base-router
      │     └── menu-main
      │           ├── menu-sub1
      │           │     └── menu-sub2
      │           └── menu-sub3
      └── fallback-router
    """

    # yapf: disable
    # root router
    assert len(router._routers) == 2  # base, fallback
    assert not router._handlers

    # base router
    assert len(router._routers[0]._routers) == 1  # main

    # main menu
    assert len(router._routers[0]._routers[0]._routers) == 2  # sub1, sub3
    assert len(router._routers[0]._routers[0]._handlers) == 2  # submenu, action
    assert router._routers[0]._routers[0]._handlers[1]._fn is action2

    # sub1 router
    assert len(router._routers[0]._routers[0]._routers[0]._routers) == 1  # sub2
    assert len(router._routers[0]._routers[0]._routers[0]._handlers) == 1  # back  # noqa: E501

    # sub2 router
    assert not router._routers[0]._routers[0]._routers[0]._routers[0]._routers
    assert len(router._routers[0]._routers[0]._routers[0]._routers[0]._handlers) == 1  # back  # noqa: E501

    # sub3 router
    assert not router._routers[0]._routers[0]._routers[1]._routers
    assert len(router._routers[0]._routers[0]._routers[1]._handlers) == 2  # action, back  # noqa: E501
    assert router._routers[0]._routers[0]._routers[1]._handlers[1]._fn is action1  # noqa: E501

    # fallback router
    assert not router._routers[1]._routers
    assert len(router._routers[1]._handlers) == 1
    # yapf: enable

    assert menu._parent is None
    assert menu._prefix is not None
    assert menu._rows == [
        Row([Submenu(title="sub1", menu="sub1")]),
        Row([Action(title="button2", action=action2)]),
    ]

    sub1 = menu._submenu["sub1"]
    assert sub1._parent is menu
    assert sub1._prefix is not None
    assert sub1._rows == [
        Row([Submenu(title="sub2", menu="sub2")]),
        Row([Back(title="back")]),
    ]

    sub2 = sub1._submenu["sub2"]
    assert sub2._parent is sub1
    assert sub2._prefix is not None
    assert sub2._rows == [
        Row([Back(title="back")]),
    ]

    sub3 = menu._submenu["sub3"]
    assert sub3._parent is menu
    assert sub3._prefix is not None
    assert sub3._rows == [
        Row([Action(title="button1", action=action1)]),
        Row([Back(title="back")]),
    ]
