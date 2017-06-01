from __future__ import unicode_literals
import types
from prompt_toolkit.eventloop.defaults import get_event_loop
from prompt_toolkit.eventloop.future import Future

__all__ = (
    'From',
    'Return',
    'ensure_future',
)


def ensure_future(future_or_coroutine):
    """
    Take a coroutine (generator) or a `Future` object, and make sure to return
    a `Future`.
    """
    if isinstance(future_or_coroutine, Future):
        return future_or_coroutine
    elif isinstance(future_or_coroutine, types.GeneratorType):
        return _run_coroutine(future_or_coroutine)
    else:
        raise ValueError('Expecting coroutine or Future object. Got %r' %
                         type(future_or_coroutine))


class Return(Exception):
    """
    For backwards-compatibility with Python2: when "return" is not supported in
    a generator/coroutine.  (Like Trollius.)

    Instead of ``return value``, in a coroutine do:  ``raise Return(value)``.
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Return(%r)' % (self.value, )


def From(obj):
    """
    Used to emulate 'yield from'.
    (Like Trollius does.)
    """
    return obj


def _run_coroutine(coroutine):
    """
    Takes a generator that can yield Future instances.

    Example:

        def gen():
            yield From(...)
            print('...')
            yield From(...)
        ensure_future(gen())

    The values which are yielded by the given coroutine are supposed to be
    `Future` objects.
    """
    assert isinstance(coroutine, types.GeneratorType)
    loop = get_event_loop()

    result_f = loop.create_future()

    # Loop through the generator.
    def step_next(f=None):
        " Execute next step of the coroutine."
        try:
            # Run until next yield.
            if f is None:
                new_f = coroutine.send(None)
            else:
                exc = f.exception()
                if exc:
                    new_f = coroutine.throw(exc)
                else:
                    new_f = coroutine.send(f.result())
        except StopIteration as e:
            result_f.set_result(e.args[0] if e.args else None)
        except Return as e:
            result_f.set_result(e.value)
        except BaseException as e:
            result_f.set_exception(e)
        else:
            # Process yielded value from coroutine.
            new_f = ensure_future(new_f)

            @new_f.add_done_callback
            def continue_(_):
                step_next(new_f)

    # Start processing coroutine.
    step_next()

    return result_f
