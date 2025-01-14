#!/usr/bin/env python
"""
Demonstration of all the ANSI colors.
"""
from __future__ import print_function, unicode_literals

from prompt_toolkit2 import print_formatted_text
from prompt_toolkit2.formatted_text import HTML, FormattedText
from prompt_toolkit2.output import ColorDepth

print = print_formatted_text


def main():
    print(HTML('\n<u>True color test.</u>'))

    for template in [
            'bg:#{0:02x}0000',  # Red.
            'bg:#00{0:02x}00',  # Green.
            'bg:#0000{0:02x}',  # Blue.
            'bg:#{0:02x}{0:02x}00', # Yellow.
            'bg:#{0:02x}00{0:02x}', # Magenta.
            'bg:#00{0:02x}{0:02x}', # Cyan.
            'bg:#{0:02x}{0:02x}{0:02x}', # Gray.
            ]:
        fragments = []
        for i in range(0, 256, 4):
            fragments.append((template.format(i), ' '))

        print(FormattedText(fragments), color_depth=ColorDepth.DEPTH_4_BIT)
        print(FormattedText(fragments), color_depth=ColorDepth.DEPTH_8_BIT)
        print(FormattedText(fragments), color_depth=ColorDepth.DEPTH_24_BIT)
        print()


if __name__ == '__main__':
    main()
