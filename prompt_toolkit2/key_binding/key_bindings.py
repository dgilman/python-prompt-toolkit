"""
Key bindings registry.

A `KeyBindings` object is a container that holds a list of key bindings. It has a
very efficient internal data structure for checking which key bindings apply
for a pressed key.

Typical usage::

    kb = KeyBindings()

    @kb.add(Keys.ControlX, Keys.ControlC, filter=INSERT)
    def handler(event):
        # Handle ControlX-ControlC key sequence.
        pass

It is also possible to combine multiple KeyBindings objects. We do this in the
default key bindings. There are some KeyBindings objects that contain the Emacs
bindings, while others contain the Vi bindings. They are merged together using
`merge_key_bindings`.

We also have a `ConditionalKeyBindings` object that can enable/disable a group of
key bindings at once.


It is also possible to add a filter to a function, before a key binding has
been assigned, through the `key_binding` decorator.::

    # First define a key handler with the `filter`.
    @key_binding(filter=condition)
    def my_key_binding(event):
        ...

    # Later, add it to the key bindings.
    kb.add(Keys.A, my_key_binding)
"""
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty

from six import text_type, with_metaclass

from prompt_toolkit2.cache import SimpleCache
from prompt_toolkit2.filters import Never, to_filter
from prompt_toolkit2.keys import ALL_KEYS, KEY_ALIASES, Keys

__all__ = [
    'KeyBindingsBase',
    'KeyBindings',
    'ConditionalKeyBindings',
    'merge_key_bindings',
    'DynamicKeyBindings',
    'GlobalOnlyKeyBindings',
]


class _Binding(object):
    """
    (Immutable binding class.)

    :param record_in_macro: When True, don't record this key binding when a
        macro is recorded.
    """
    def __init__(self, keys, handler, filter=True, eager=False,
                 is_global=False, save_before=None, record_in_macro=True):
        assert isinstance(keys, tuple)
        assert callable(handler)
        assert callable(save_before)

        self.keys = keys
        self.handler = handler
        self.filter = to_filter(filter)
        self.eager = to_filter(eager)
        self.is_global = to_filter(is_global)
        self.save_before = save_before
        self.record_in_macro = to_filter(record_in_macro)

    def call(self, event):
        return self.handler(event)

    def __repr__(self):
        return '%s(keys=%r, handler=%r)' % (
            self.__class__.__name__, self.keys, self.handler)


class KeyBindingsBase(with_metaclass(ABCMeta, object)):
    """
    Interface for a KeyBindings.
    """
    @abstractproperty
    def _version(self):
        """
        For cache invalidation. - This should increase every time that
        something changes.
        """
        return 0

    @abstractmethod
    def get_bindings_for_keys(self, keys):
        """
        Return a list of key bindings that can handle these keys.
        (This return also inactive bindings, so the `filter` still has to be
        called, for checking it.)

        :param keys: tuple of keys.
        """
        return []

    @abstractmethod
    def get_bindings_starting_with_keys(self, keys):
        """
        Return a list of key bindings that handle a key sequence starting with
        `keys`. (It does only return bindings for which the sequences are
        longer than `keys`. And like `get_bindings_for_keys`, it also includes
        inactive bindings.)

        :param keys: tuple of keys.
        """
        return []

    # `add` and `remove` don't have to be part of this interface.


class KeyBindings(KeyBindingsBase):
    """
    A container for a set of key bindings.

    Example usage::

        kb = KeyBindings()

        @kb.add('c-t')
        def _(event):
            print('Control-T pressed')

        @kb.add('c-a', 'c-b')
        def _(event):
            print('Control-A pressed, followed by Control-B')

        @kb.add('c-x', filter=is_searching)
        def _(event):
            print('Control-X pressed')  # Works only if we are searching.

    """
    def __init__(self):
        self.bindings = []
        self._get_bindings_for_keys_cache = SimpleCache(maxsize=10000)
        self._get_bindings_starting_with_keys_cache = SimpleCache(maxsize=1000)
        self.__version = 0  # For cache invalidation.

    def _clear_cache(self):
        self.__version += 1
        self._get_bindings_for_keys_cache.clear()
        self._get_bindings_starting_with_keys_cache.clear()

    @property
    def _version(self):
        return self.__version

    def add(self, *keys, **kwargs):
        """
        Decorator for adding a key bindings.

        :param filter: :class:`~prompt_toolkit.filters.Filter` to determine
            when this key binding is active.
        :param eager: :class:`~prompt_toolkit.filters.Filter` or `bool`.
            When True, ignore potential longer matches when this key binding is
            hit. E.g. when there is an active eager key binding for Ctrl-X,
            execute the handler immediately and ignore the key binding for
            Ctrl-X Ctrl-E of which it is a prefix.
        :param is_global: When this key bindings is added to a `Container` or
            `Control`, make it a global (always active) binding.
        :param save_before: Callable that takes an `Event` and returns True if
            we should save the current buffer, before handling the event.
            (That's the default.)
        :param record_in_macro: Record these key bindings when a macro is
            being recorded. (True by default.)
        """
        filter = to_filter(kwargs.pop('filter', True))
        eager = to_filter(kwargs.pop('eager', False))
        is_global = to_filter(kwargs.pop('is_global', False))
        save_before = kwargs.pop('save_before', lambda e: True)
        record_in_macro = to_filter(kwargs.pop('record_in_macro', True))

        assert not kwargs
        assert keys
        assert callable(save_before)

        keys = tuple(_check_and_expand_key(k) for k in keys)

        if isinstance(filter, Never):
            # When a filter is Never, it will always stay disabled, so in that
            # case don't bother putting it in the key bindings. It will slow
            # down every key press otherwise.
            def decorator(func):
                return func
        else:
            def decorator(func):
                if isinstance(func, _Binding):
                    # We're adding an existing _Binding object.
                    self.bindings.append(
                        _Binding(
                            keys, func.handler,
                            filter=func.filter & filter,
                            eager=eager | func.eager,
                            is_global = is_global | func.is_global,
                            save_before=func.save_before,
                            record_in_macro=func.record_in_macro))
                else:
                    self.bindings.append(
                        _Binding(keys, func, filter=filter, eager=eager,
                                 is_global=is_global, save_before=save_before,
                                 record_in_macro=record_in_macro))
                self._clear_cache()

                return func
        return decorator

    def remove(self, *args):
        """
        Remove a key binding.

        This expects either a function that was given to `add` method as
        parameter or a sequence of key bindings.

        Raises `ValueError` when no bindings was found.

        Usage::

            remove(handler)  # Pass handler.
            remove('c-x', 'c-a')  # Or pass the key bindings.
        """
        found = False

        if callable(args[0]):
            assert len(args) == 1
            function = args[0]

            # Remove the given function.
            for b in self.bindings:
                if b.handler == function:
                    self.bindings.remove(b)
                    found = True

        else:
            assert len(args) > 0

            # Remove this sequence of key bindings.
            keys = tuple(_check_and_expand_key(k) for k in args)

            for b in self.bindings:
                if b.keys == keys:
                    self.bindings.remove(b)
                    found = True

        if found:
            self._clear_cache()
        else:
            # No key binding found for this function. Raise ValueError.
            raise ValueError('Binding not found: %r' % (function, ))

    # For backwards-compatibility.
    add_binding = add
    remove_binding = remove

    def get_bindings_for_keys(self, keys):
        """
        Return a list of key bindings that can handle this key.
        (This return also inactive bindings, so the `filter` still has to be
        called, for checking it.)

        :param keys: tuple of keys.
        """
        def get():
            result = []
            for b in self.bindings:
                if len(keys) == len(b.keys):
                    match = True
                    any_count = 0

                    for i, j in zip(b.keys, keys):
                        if i != j and i != Keys.Any:
                            match = False
                            break

                        if i == Keys.Any:
                            any_count += 1

                    if match:
                        result.append((any_count, b))

            # Place bindings that have more 'Any' occurrences in them at the end.
            result = sorted(result, key=lambda item: -item[0])

            return [item[1] for item in result]

        return self._get_bindings_for_keys_cache.get(keys, get)

    def get_bindings_starting_with_keys(self, keys):
        """
        Return a list of key bindings that handle a key sequence starting with
        `keys`. (It does only return bindings for which the sequences are
        longer than `keys`. And like `get_bindings_for_keys`, it also includes
        inactive bindings.)

        :param keys: tuple of keys.
        """
        def get():
            result = []
            for b in self.bindings:
                if len(keys) < len(b.keys):
                    match = True
                    for i, j in zip(b.keys, keys):
                        if i != j and i != Keys.Any:
                            match = False
                            break
                    if match:
                        result.append(b)
            return result

        return self._get_bindings_starting_with_keys_cache.get(keys, get)


def _check_and_expand_key(key):
    """
    Replace key by alias and verify whether it's a valid one.
    """
    # Lookup aliases.
    key = KEY_ALIASES.get(key, key)

    # Replace 'space' by ' '
    if key == 'space':
        key = ' '

    # Final validation.
    assert isinstance(key, text_type), 'Got %r' % (key, )
    if len(key) != 1 and key not in ALL_KEYS:
        raise ValueError('Invalid key: %s' % (key, ))

    return key


def key_binding(filter=True, eager=False, is_global=False, save_before=None,
                record_in_macro=True):
    """
    Decorator that turn a function into a `_Binding` object. This can be added
    to a `KeyBindings` object when a key binding is assigned.
    """
    assert save_before is None or callable(save_before)

    filter = to_filter(filter)
    eager = to_filter(eager)
    is_global = to_filter(is_global)
    save_before = save_before or (lambda event: True)
    record_in_macro = to_filter(record_in_macro)
    keys = ()

    def decorator(function):
        return _Binding(keys, function, filter=filter, eager=eager,
                        is_global=is_global, save_before=save_before,
                        record_in_macro=record_in_macro)

    return decorator


class _Proxy(KeyBindingsBase):
    """
    Common part for ConditionalKeyBindings and _MergedKeyBindings.
    """
    def __init__(self):
        # `KeyBindings` to be synchronized with all the others.
        self._bindings2 = KeyBindings()
        self._last_version = None

    def _update_cache(self):
        """
        If `self._last_version` is outdated, then this should update
        the version and `self._bindings2`.
        """
        raise NotImplementedError

    # Proxy methods to self._bindings2.

    @property
    def bindings(self):
        self._update_cache()
        return self._bindings2.bindings

    @property
    def _version(self):
        self._update_cache()
        return self._last_version

    def get_bindings_for_keys(self, *a, **kw):
        self._update_cache()
        return self._bindings2.get_bindings_for_keys(*a, **kw)

    def get_bindings_starting_with_keys(self, *a, **kw):
        self._update_cache()
        return self._bindings2.get_bindings_starting_with_keys(*a, **kw)


class ConditionalKeyBindings(_Proxy):
    """
    Wraps around a `KeyBindings`. Disable/enable all the key bindings according to
    the given (additional) filter.::

        @Condition
        def setting_is_true():
            return True  # or False

        registry = ConditionalKeyBindings(key_bindings, setting_is_true)

    When new key bindings are added to this object. They are also
    enable/disabled according to the given `filter`.

    :param registries: List of :class:`.KeyBindings` objects.
    :param filter: :class:`~prompt_toolkit.filters.Filter` object.
    """
    def __init__(self, key_bindings, filter=True):
        assert isinstance(key_bindings, KeyBindingsBase)
        _Proxy.__init__(self)

        self.key_bindings = key_bindings
        self.filter = to_filter(filter)

    def _update_cache(self):
        " If the original key bindings was changed. Update our copy version. "
        expected_version = self.key_bindings._version

        if self._last_version != expected_version:
            bindings2 = KeyBindings()

            # Copy all bindings from `self.key_bindings`, adding our condition.
            for b in self.key_bindings.bindings:
                bindings2.bindings.append(
                    _Binding(
                        keys=b.keys,
                        handler=b.handler,
                        filter=self.filter & b.filter,
                        eager=b.eager,
                        is_global=b.is_global,
                        save_before=b.save_before,
                        record_in_macro=b.record_in_macro))

            self._bindings2 = bindings2
            self._last_version = expected_version


class _MergedKeyBindings(_Proxy):
    """
    Merge multiple registries of key bindings into one.

    This class acts as a proxy to multiple :class:`.KeyBindings` objects, but
    behaves as if this is just one bigger :class:`.KeyBindings`.

    :param registries: List of :class:`.KeyBindings` objects.
    """
    def __init__(self, registries):
        assert all(isinstance(r, KeyBindingsBase) for r in registries)
        _Proxy.__init__(self)
        self.registries = registries

    def _update_cache(self):
        """
        If one of the original registries was changed. Update our merged
        version.
        """
        expected_version = tuple(r._version for r in self.registries)

        if self._last_version != expected_version:
            bindings2 = KeyBindings()

            for reg in self.registries:
                bindings2.bindings.extend(reg.bindings)

            self._bindings2 = bindings2
            self._last_version = expected_version


def merge_key_bindings(bindings):
    """
    Merge multiple :class:`.Keybinding` objects together.

    Usage::

        bindings = merge_key_bindings([bindings1, bindings2, ...])
    """
    return _MergedKeyBindings(bindings)


class DynamicKeyBindings(_Proxy):
    """
    KeyBindings class that can dynamically returns any KeyBindings.

    :param get_key_bindings: Callable that returns a :class:`.KeyBindings` instance.
    """
    def __init__(self, get_key_bindings):
        assert callable(get_key_bindings)
        self.get_key_bindings = get_key_bindings
        self.__version = 0
        self._last_child_version = None
        self._dummy = KeyBindings()  # Empty key bindings.

    def _update_cache(self):
        key_bindings = self.get_key_bindings() or self._dummy
        assert isinstance(key_bindings, KeyBindingsBase)
        version = id(key_bindings), key_bindings._version

        self._bindings2 = key_bindings
        self._last_version = version


class GlobalOnlyKeyBindings(_Proxy):
    """
    Wrapper around a :class:`.KeyBindings` object that only exposes the global
    key bindings.
    """
    def __init__(self, key_bindings):
        assert isinstance(key_bindings, KeyBindingsBase)
        _Proxy.__init__(self)
        self.key_bindings = key_bindings

    def _update_cache(self):
        """
        If one of the original registries was changed. Update our merged
        version.
        """
        expected_version = self.key_bindings._version

        if self._last_version != expected_version:
            bindings2 = KeyBindings()

            for b in self.key_bindings.bindings:
                if b.is_global():
                    bindings2.bindings.append(b)

            self._bindings2 = bindings2
            self._last_version = expected_version
