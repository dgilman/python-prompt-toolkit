#!/usr/bin/env python
"""
Autocompletion example that displays the autocompletions like readline does by
binding a custom handler to the Tab key.
"""
from __future__ import unicode_literals

from prompt_toolkit2.completion import WordCompleter
from prompt_toolkit2.shortcuts import CompleteStyle, prompt

animal_completer = WordCompleter([
    'alligator', 'ant', 'ape', 'bat', 'bear', 'beaver', 'bee', 'bison',
    'butterfly', 'cat', 'chicken', 'crocodile', 'dinosaur', 'dog', 'dolphin',
    'dove', 'duck', 'eagle', 'elephant', 'fish', 'goat', 'gorilla', 'kangaroo',
    'leopard', 'lion', 'mouse', 'rabbit', 'rat', 'snake', 'spider', 'turkey',
    'turtle',
], ignore_case=True)


def main():
    text = prompt('Give some animals: ', completer=animal_completer,
                  complete_style=CompleteStyle.READLINE_LIKE)
    print('You said: %s' % text)


if __name__ == '__main__':
    main()
