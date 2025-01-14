#!/usr/bin/env python
"""
Demonstration of all the ANSI colors.
"""
from __future__ import print_function, unicode_literals

from prompt_toolkit2 import HTML, print_formatted_text
from prompt_toolkit2.formatted_text import FormattedText
from prompt_toolkit2.output import ColorDepth
from prompt_toolkit2.styles.named_colors import NAMED_COLORS

print = print_formatted_text


def main():
    tokens = FormattedText(
        [('fg:' + name, name + '  ') for name in NAMED_COLORS]
    )

    print(HTML('\n<u>Named colors, using 16 color output.</u>'))
    print('(Note that it doesn\'t really make sense to use named colors ')
    print('with only 16 color output.)')
    print(tokens, color_depth=ColorDepth.DEPTH_4_BIT)

    print(HTML('\n<u>Named colors, use 256 colors.</u>'))
    print(tokens)

    print(HTML('\n<u>Named colors, using True color output.</u>'))
    print(tokens, color_depth=ColorDepth.TRUE_COLOR)


if __name__ == '__main__':
    main()
