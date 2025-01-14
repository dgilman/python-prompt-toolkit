#!/usr/bin/env python
"""
Example usage of 'print_container', a tool to print
any layout in a non-interactive way.
"""
from __future__ import print_function, unicode_literals

from prompt_toolkit2.shortcuts import print_container
from prompt_toolkit2.widgets import Frame, TextArea

print_container(
    Frame(
        TextArea(text='Hello world!\n'),
        title='Stage: parse',
    ))
