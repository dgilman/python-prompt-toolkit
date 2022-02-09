#!/usr/bin/env python
"""
Demonstration of how the input can be indented.
"""
from __future__ import unicode_literals

from prompt_toolkit2 import prompt

if __name__ == '__main__':
    answer = prompt('Give me some input: (ESCAPE followed by ENTER to accept)\n > ', multiline=True)
    print('You said: %s' % answer)
