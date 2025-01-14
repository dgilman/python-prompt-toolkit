#!/usr/bin/env python
"""
Horizontal split example.
"""
from __future__ import unicode_literals

from prompt_toolkit2.application import Application
from prompt_toolkit2.key_binding import KeyBindings
from prompt_toolkit2.layout.containers import HSplit, Window
from prompt_toolkit2.layout.controls import FormattedTextControl
from prompt_toolkit2.layout.layout import Layout

# 1. The layout
left_text = "\nVertical-split example. Press 'q' to quit.\n\n(top pane.)"
right_text = "\n(bottom pane.)"


body = HSplit([
    Window(FormattedTextControl(left_text)),
    Window(height=1, char='-'),  # Horizontal line in the middle.
    Window(FormattedTextControl(right_text)),
])


# 2. Key bindings
kb = KeyBindings()


@kb.add('q')
def _(event):
    " Quit application. "
    event.app.exit()


# 3. The `Application`
application = Application(
    layout=Layout(body),
    key_bindings=kb,
    full_screen=True)


def run():
    application.run()


if __name__ == '__main__':
    run()
