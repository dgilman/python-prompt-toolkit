#!/usr/bin/env python
"""
The most simple prompt example.
"""
from __future__ import unicode_literals

from prompt_toolkit2 import prompt

if __name__ == '__main__':
    answer = prompt('Give me some input: ')
    print('You said: %s' % answer)
