import pytest

from yatbaf_menu.button import URL
from yatbaf_menu.button import Back
from yatbaf_menu.menu import _parse_markup
from yatbaf_menu.row import Choice
from yatbaf_menu.row import Row


@pytest.mark.parametrize(
    "markup,expected",
    [
        (
            [
                Choice(action=(a := object()), items=[1, 2, 3]),
                Back(title="back"),
            ],
            [
                Choice(action=a, items=[1, 2, 3]),
                Row([Back(title="back")]),
            ],
        ),
        (
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
                Row([
                    URL(url="example.com", title="example 1"),
                    URL(url="example.com", title="example 2"),
                ]),
                Row([
                    URL(url="example.com", title="example 3"),
                    URL(url="example.com", title="example 4"),
                ]),
            ],
        ),
        (
            [
                URL(url="example.com", title="example 1"),
                URL(url="example.com", title="example 2"),
                URL(url="example.com", title="example 3"),
                URL(url="example.com", title="example 4"),
            ],
            [
                Row([URL(url="example.com", title="example 1")]),
                Row([URL(url="example.com", title="example 2")]),
                Row([URL(url="example.com", title="example 3")]),
                Row([URL(url="example.com", title="example 4")]),
            ],
        ),
        (
            [
                [
                    Row([
                        URL(url="example.com", title="example 1"),
                        URL(url="example.com", title="example 2"),
                    ]),
                ],
                URL(url="example.com", title="example 3"),
                URL(url="example.com", title="example 4"),
            ],
            [
                Row([
                    URL(url="example.com", title="example 1"),
                    URL(url="example.com", title="example 2"),
                ]),
                Row([URL(url="example.com", title="example 3")]),
                Row([URL(url="example.com", title="example 4")]),
            ],
        ),
        (
            [[Choice(submenu="qwe", items=[1, 2, 3])]],
            [Choice(submenu="qwe", items=[1, 2, 3])],
        ),
    ]
)
def test_parse_markup(markup, expected):
    assert _parse_markup(markup) == expected


def test_error():
    with pytest.raises(ValueError):
        _parse_markup([
            [
                Choice(submenu="qwe", items=[1, 2, 3]),
                Choice(submenu="ewq", items=[3, 2, 1]),
            ],
        ])
