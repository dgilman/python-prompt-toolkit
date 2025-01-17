#!/usr/bin/env python
"""
A simple progress bar, visualised with rainbow colors (for fun).
"""
from __future__ import unicode_literals

import time

from prompt_toolkit2.output import ColorDepth
from prompt_toolkit2.shortcuts import ProgressBar
from prompt_toolkit2.shortcuts.progress_bar import formatters
from prompt_toolkit2.shortcuts.prompt import confirm


def main():
    true_color = confirm('Yes true colors? (y/n) ')

    custom_formatters = [
        formatters.Label(),
        formatters.Text(' '),
        formatters.Rainbow(formatters.Bar()),
        formatters.Text(' left: '),
        formatters.Rainbow(formatters.TimeLeft()),
    ]

    if true_color:
        color_depth = ColorDepth.DEPTH_24_BIT
    else:
        color_depth = ColorDepth.DEPTH_8_BIT

    with ProgressBar(formatters=custom_formatters, color_depth=color_depth) as pb:
        for i in pb(range(20), label='Downloading...'):
            time.sleep(1)


if __name__ == '__main__':
    main()
