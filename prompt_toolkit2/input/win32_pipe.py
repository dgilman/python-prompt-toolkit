from ctypes import windll

from prompt_toolkit2.eventloop.win32 import create_win32_event

from ..utils import DummyContext
from .base import Input
from .vt100_parser import Vt100Parser
from .win32 import attach_win32_input, detach_win32_input

__all__ = [
    'Win32PipeInput'
]


class Win32PipeInput(Input):
    """
    This is an input pipe that works on Windows.
    Text or bytes can be feed into the pipe, and key strokes can be read from
    the pipe. This is useful if we want to send the input programmatically into
    the application. Mostly useful for unit testing.

    Notice that even though it's Windows, we use vt100 escape sequences over
    the pipe.

    Usage::

        input = Win32PipeInput()
        input.send_text('inputdata')
    """
    _id = 0
    def __init__(self):
        # Event (handle) for registering this input in the event loop.
        # This event is set when there is data available to read from the pipe.
        # Note: We use this approach instead of using a regular pipe, like
        #       returned from `os.pipe()`, because making such a regular pipe
        #       non-blocking is tricky and this works really well.
        self._event = create_win32_event()

        self._closed = False

        # Parser for incoming keys.
        self._buffer = []  # Buffer to collect the Key objects.
        self.vt100_parser = Vt100Parser(
            lambda key: self._buffer.append(key))

        # Identifier for every PipeInput for the hash.
        self.__class__._id += 1
        self._id = self.__class__._id

    @property
    def closed(self):
        return self._closed

    def fileno(self):
        """
        The windows pipe doesn't depend on the file handle.
        """
        raise NotImplementedError

    @property
    def handle(self):
        " The handle used for registering this pipe in the event loop. "
        return self._event

    def attach(self, input_ready_callback):
        """
        Return a context manager that makes this input active in the current
        event loop.
        """
        assert callable(input_ready_callback)
        return attach_win32_input(self, input_ready_callback)

    def detach(self):
        """
        Return a context manager that makes sure that this input is not active
        in the current event loop.
        """
        return detach_win32_input(self)

    def read_keys(self):
        " Read list of KeyPress. "

        # Return result.
        result = self._buffer
        self._buffer = []

        # Reset event.
        windll.kernel32.ResetEvent(self._event)

        return result

    def flush_keys(self):
        """
        Flush pending keys and return them.
        (Used for flushing the 'escape' key.)
        """
        # Flush all pending keys. (This is most important to flush the vt100
        # 'Escape' key early when nothing else follows.)
        self.vt100_parser.flush()

        # Return result.
        result = self._buffer
        self._buffer = []
        return result

    @property
    def responds_to_cpr(self):
        return False

    def send_bytes(self, data):
        " Send bytes to the input. "
        self.send_text(data.decode('utf-8', 'ignore'))

    def send_text(self, text):
        " Send text to the input. "
        # Pass it through our vt100 parser.
        self.vt100_parser.feed(text)

        # Set event.
        windll.kernel32.SetEvent(self._event)

    def raw_mode(self):
        return DummyContext()

    def cooked_mode(self):
        return DummyContext()

    def close(self):
        " Close pipe handles. "
        windll.kernel32.CloseHandle(self._event)
        self._closed = True

    def typeahead_hash(self):
        """
        This needs to be unique for every `PipeInput`.
        """
        return 'pipe-input-%s' % (self._id, )
