#!/usr/bin/env python
"""
An example of a BufferControl in a full screen layout that offers auto
completion.

Important is to make sure that there is a `CompletionsMenu` in the layout,
otherwise the completions won't be visible.
"""
from __future__ import unicode_literals

from prompt_toolkit2.application import Application
from prompt_toolkit2.buffer import Buffer
from prompt_toolkit2.completion import WordCompleter
from prompt_toolkit2.key_binding import KeyBindings
from prompt_toolkit2.layout.containers import (
    Float,
    FloatContainer,
    HSplit,
    Window,
)
from prompt_toolkit2.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit2.layout.layout import Layout
from prompt_toolkit2.layout.menus import CompletionsMenu

# The completer.
animal_completer = WordCompleter([
    'alligator', 'ant', 'ape', 'bat', 'bear', 'beaver', 'bee', 'bison',
    'butterfly', 'cat', 'chicken', 'crocodile', 'dinosaur', 'dog', 'dolphin',
    'dove', 'duck', 'eagle', 'elephant', 'fish', 'goat', 'gorilla', 'kangaroo',
    'leopard', 'lion', 'mouse', 'rabbit', 'rat', 'snake', 'spider', 'turkey',
    'turtle',
], ignore_case=True)


# The layout
buff = Buffer(completer=animal_completer, complete_while_typing=True)

body = FloatContainer(
    content=HSplit([
        Window(FormattedTextControl('Press "q" to quit.'), height=1, style='reverse'),
        Window(BufferControl(buffer=buff)),
    ]),
    floats=[
        Float(xcursor=True,
              ycursor=True,
              content=CompletionsMenu(max_height=16, scroll_offset=1))
    ]
)


# Key bindings
kb = KeyBindings()


@kb.add('q')
@kb.add('c-c')
def _(event):
    " Quit application. "
    event.app.exit()


# The `Application`
application = Application(
    layout=Layout(body),
    key_bindings=kb,
    full_screen=True)


def run():
    application.run()


if __name__ == '__main__':
    run()
