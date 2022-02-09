#!/usr/bin/env python
"""
Example of a telnet application that displays a dialog window.
"""
from __future__ import unicode_literals

import logging

from prompt_toolkit2.contrib.telnet.server import TelnetServer
from prompt_toolkit2.eventloop import From, get_event_loop
from prompt_toolkit2.shortcuts.dialogs import yes_no_dialog

# Set up logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def interact(connection):
    result = yield From(yes_no_dialog(
        title='Yes/no dialog demo', text='Press yes or no', async_=True))

    connection.send('You said: {}\n'.format(result))
    connection.send('Bye.\n')


def main():
    server = TelnetServer(interact=interact, port=2323)
    server.start()
    get_event_loop().run_forever()


if __name__ == '__main__':
    main()
