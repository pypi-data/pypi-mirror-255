## yatbaf-menu

Inline menu builder for [yatbaf](https://codeberg.org/maraudeur/yatbaf).

## Installation

```shell
$ pip install yatbaf-menu
```

## Usage

```python
from typing import TYPE_CHECKING

from yatbaf import Bot
from yatbaf import on_message
from yatbaf.filters import Command

from yatbaf_menu import Action
from yatbaf_menu import Menu
from yatbaf_menu import build_router

if TYPE_CHECKING:
    from yatbaf.types import CallbackQuery
    from yatbaf.types import Message



async def button1(q: CallbackQuery) -> None:
    await q.answer()
    await q.message.answer("click1")


async def button2(q: CallbackQuery) -> None:
    await q.answer()
    await q.message.answer("click2")


menu = Menu(
    title="Menu title",
    buttons=[
        [
            Action(title="Click 1", action=button1),
            Action(title="Click 2", action=button2),
        ],
    ],
)


@on_message(filters=[Command("menu")])
async def open_menu(message: Message) -> None:
    await message.answer(**(await menu.get_message_params(message)))


Bot(
    "<replace-with-your-token>",
    handlers=[open_menu],
    routers=[build_router(menu)],
).run()
```

## Examples

### Click
Click action

![click gif](media/click.gif)

[code](examples/click.py)

### URL
URL button

![url pic](media/url.webp)

[code](examples/url.py)

### Submenu
Submenu button

![submenu gif](media/submenu.gif)

[code](examples/submenu.py)

### Choice

![choice gif](media/choice.gif)

[code](examples/choice.py)

### Pagination

![paging gif](media/paging.gif)

[code](examples/paging.py)

### Dynamic titles and visibility

![dynamic gif](media/dynamic.gif)

[code](examples/dynamic.py)

## License
[MIT](./LICENSE)
