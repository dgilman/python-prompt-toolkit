#!/usr/bin/env python
"""
A simple Telnet application that asks for input and responds.

The interaction function is a prompt_toolkit coroutine.
Also see the `hello-world-asyncio.py` example which uses an asyncio coroutine.
That is probably the preferred way if you only need Python 3 support.
"""
from __future__ import unicode_literals

import logging

from prompt_toolkit2.contrib.telnet.server import TelnetServer
from prompt_toolkit2.eventloop import From, get_event_loop
from prompt_toolkit2.shortcuts import clear, prompt

# Set up logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def interact(connection):
    clear()
    connection.send('Welcome!\n')

    # Ask for input.
    result = yield From(prompt(message='Say something: ', async_=True))

    # Send output.
    connection.send('You said: {}\n'.format(result))
    connection.send('Bye.\n')


def main():
    server = TelnetServer(interact=interact, port=2323)
    server.start()
    get_event_loop().run_forever()


if __name__ == '__main__':
    main()
