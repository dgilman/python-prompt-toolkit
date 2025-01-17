#!/usr/bin/env python
"""
A progress bar that displays a formatted title above the progress bar and has a
colored label.
"""
from __future__ import unicode_literals

import time

from prompt_toolkit2.formatted_text import HTML
from prompt_toolkit2.shortcuts import ProgressBar


def main():
    title = HTML('Downloading <style bg="yellow" fg="black">4 files...</style>')
    label = HTML('<ansired>some file</ansired>: ')

    with ProgressBar(title=title) as pb:
        for i in pb(range(800), label=label):
            time.sleep(.01)


if __name__ == '__main__':
    main()
