#!/usr/bin/env python
"""
A very simple progress bar which keep track of the progress as we consume an
iterator.
"""
from __future__ import unicode_literals

import time

from prompt_toolkit2.shortcuts import ProgressBar


def main():
    with ProgressBar() as pb:
        for i in pb(range(800)):
            time.sleep(.01)


if __name__ == '__main__':
    main()
