"""Generic helper methods

Nothing here is dependent on Red, and as such can safely be used in other projects.
"""

from __future__ import annotations

import collections
import logging
from asyncio import Queue
from contextlib import contextmanager
import copy
from datetime import datetime, timedelta
from typing import (
    Any,
    AsyncIterable,
    Callable,
    MutableMapping,
    Sequence,
    Tuple,
    Union,
    Dict,
    Iterable,
    TypeVar,
    List,
    Mapping,
)

from .consts import undefined

__all__ = (
    "flatten",
    "unflatten_dict",
    "replace_dict_values",
    "replace_list_values",
    "DefaultDict",
    "chunks",
    "timer",
    "runtime_data",
    "ExtendedQueue",
    "TimeCache",
    "deep_merge",
    "alist",
)

# TODO: should dict/list-related methods be moved to a separate file?
#       currently, this is arguably the largest file in swift_libs, and it's almost
#       entirely dominated by these such methods.

# noinspection PyShadowingBuiltins
_T = TypeVar("_T")
_runtime_data = {}


def runtime_data(cog: str) -> dict:
    """Get a semi-persistent dict to store runtime data

    This dict only survives between simple cog reloads, not full restarts. If you're looking for
    more persistent data storage, you should use :class:`~redbot.core.config.Config` instead.

    If swift_libs is reloaded, this dict will be lost.
    """
    if cog not in _runtime_data:
        _runtime_data[cog] = {}
    return _runtime_data[cog]


class DefaultDict(dict):
    """A :class:`dict` subclass which creates new key-value pairs with a default value on access

    .. important::
        Defaults are shallowly copied if possible. Dict values and list items are not copied,
        which means any updates to mutable default values will be reflected by every default.

    Example
    -------
    >>> d = DefaultDict(default={})
    >>> 'a' in d
    False
    >>> d['a']
    {}
    >>> 'a' in d
    True
    >>> d['b']['key'] = 'value'
    >>> d['b']
    {'key': 'value'}
    >>> d
    {'a': {}, 'b': {'key': 'value'}}
    """

    def __init__(self, default, *args, **kwargs):
        self.__default = default
        super().__init__(*args, **kwargs)

    def setdefault(self, key, default=...):
        if key in self:
            return super().__getitem__(key)

        if default is ...:
            default = self.__default
            try:
                default = copy.copy(default)
            except copy.Error:
                pass
        return super().setdefault(key, default)

    __getitem__ = setdefault


class TimeCache(collections.abc.MutableMapping):
    """Simple time-based dict-like cache

    .. important::
        This determines when to remove an item based on when it was created or
        last updated, not when it was last accessed.

    Parameters
    ----------
    ttl: :class:`~datetime.timedelta`
        How long an item is allowed to exist for
    """

    def __init__(self, ttl: timedelta):
        super().__init__()
        self._data: Dict[Any, Tuple[datetime, Any]] = {}
        self.ttl = ttl

    def _maybe_invalidate(self, k):
        if k in self._data and datetime.utcnow() >= self._data[k][0] + self.ttl:
            del self[k]

    def _prune(self):
        for k in list(self._data.keys()):
            self._maybe_invalidate(k)

    def _actual_dict(self):
        return {k: v[1] for k, v in self._data.items()}

    def put(self, k, v, timestamp: datetime = None):
        self._data[k] = (timestamp if isinstance(timestamp, datetime) else datetime.utcnow(), v)

    def __getitem__(self, k):
        self._maybe_invalidate(k)
        return self._data[k][1]

    def __setitem__(self, k, v):
        self._data[k] = (datetime.utcnow(), v)

    def __delitem__(self, k):
        del self._data[k]

    def __contains__(self, k):
        self._maybe_invalidate(k)
        return k in self._data

    def __len__(self) -> int:
        self._prune()
        return len(self._data)

    def __iter__(self):
        self._prune()
        yield from self._data

    def get(self, k, default=None):  # pylint:disable=arguments-differ
        try:
            return self[k]
        except KeyError:
            return default

    def keys(self):
        self._prune()
        return self._data.keys()

    def values(self):
        self._prune()
        return self._actual_dict().values()

    def items(self):
        self._prune()
        return self._actual_dict().items()


def deep_merge(source: dict, destination: dict, *, merge_lists: Union[bool, Sequence[str]] = False):
    """Deep merge ``source`` into ``destination``

    .. warning::
        This modifies ``destination`` in place. You should :func:`~copy.deepcopy` your destination
        if you need an unmodified copy of it.

    Parameters
    ----------
    source: dict
        The source dict to deep merge on top of ``destination``
    destination: dict
        The dict to merge ``source`` onto. **This dict is modified in-place!**
    merge_lists: Union[bool, Sequence[str]]
        If this is :obj:`True`, lists will be merged if they exist in both ``source`` and
        ``destination``; if this is a sequence of :class:`str` items, lists will only
        be merged if the key for a given list is in the sequence. This applies to *every* nested
        dict.

    Returns
    -------
    dict
        The now deep merged ``destination``
    """
    # original: https://stackoverflow.com/a/20666342
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deep_merge(value, node, merge_lists=merge_lists)
        elif (
            merge_lists
            and isinstance(value, list)
            and key in destination
            and isinstance(destination[key], list)
            and (not isinstance(merge_lists, Sequence) or key in merge_lists)
        ):
            for item in value:
                if item in destination[key]:
                    continue
                destination[key].append(item)
        else:
            destination[key] = value

    return destination


def replace_dict_values(
    dct: Mapping, replace_with=undefined, converter: Callable[[Any], Any] = undefined
) -> dict:
    """Replace all values in a given :class:`dict`

    Parameters
    ----------
    dct: :class:`dict`
        The dict to replace the values in
    replace_with: Any
        The value to use
    converter: Callable[[Any], Any]
        A converter function to use. Expected to take the value being replaced as a single argument.

    Returns
    -------
    :class:`dict`
        A new dict containing the replaced values
    """
    if replace_with is undefined and converter is None:
        raise RuntimeError("Expected either `value` or `converter` to be passed, got neither")

    return {
        k: replace_dict_values(v, converter=converter, replace_with=replace_with)
        if isinstance(v, Mapping)
        else converter(v)
        if converter
        else replace_with
        for k, v in dct.items()
    }


def replace_list_values(
    lst: list, *, converter: Callable[[Any], Any] = None, value=undefined
) -> Sequence:
    """Replace all values in the given list

    Parameters
    ----------
    lst: :class:`list`
        The list to replace items in
    converter: Callable[[Any], Any]
        Optional converter function. Either this or ``value`` must be passed.
    value: Any
        The value to replace list items with. Either this or ``converter`` must be passed.

    Returns
    -------
    :class:`list`
        A list containing the updated values
    """
    if value is undefined and converter is None:
        raise RuntimeError("Expected either `value` or `converter` to be passed, got neither")

    return [
        replace_list_values(v, converter=converter, value=value)
        if isinstance(v, list)
        else converter(v)
        if converter
        else value
        for v in lst
    ]


def unflatten_dict(d: Dict[str, Any], sep: str = ".") -> dict:
    # noinspection PyUnresolvedReferences
    """Reverses flattening done on mappings by :func:`flatten`

    Example
    -------
    >>> flatten({'hello': {'world': '!'}})
    {'hello.world': '!'}
    >>> unflatten_dict(_)
    {'hello': {'world': '!'}}
    >>> flatten(_, sep='#')
    {'hello#world': '!'}
    >>> unflatten_dict(_, sep='#')
    {'hello': {'world': '!'}}

    Parameters
    ----------
    d: Dict[str, Any]
        A dict containing items with str keys separated by ``sep``
    sep: str
        The separator string that was originally used when flattening the given dict

    Returns
    -------
    dict
        The now un-flattened dict
    """
    new = {}

    for k, v in d.items():
        k = k.split(sep)
        new_ = new
        for x in k[:-1]:
            if x not in new_:
                new_[x] = {}
            new_ = new_[x]
        new_[k[-1]] = v

    return new


def flatten_dict(dct: MutableMapping[str, Any], parent_key: str = "", sep: str = "."):
    # originally from https://stackoverflow.com/a/6027615
    for k, v in dct.items():
        new_key = parent_key + sep + str(k) if parent_key else str(k)
        if isinstance(v, MutableMapping):
            yield from flatten_dict(v, new_key, sep=sep)
        else:
            yield (new_key, v)


def flatten_list(lst: Sequence[Any]):
    for item in lst:
        if isinstance(item, (list, tuple, set)):
            yield from flatten_list(item)
        else:
            yield item


def flatten(to_flatten: Union[MutableMapping, Sequence], sep: str = ".") -> Union[dict, list]:
    """Flatten a dict or sequence to one level

    Example
    -------

    On dicts::

        >>> flatten({'a': {'b': {'c': 'd'}}})
        {'a.b.c': 'd'}
        >>> flatten({'hello': {'world': '!'}}, sep='__')
        {'hello__world': '!'}

    On lists::

        >>> flatten([[1], [[2], 3], 4, [5]])
        [1, 2, 3, 4, 5]

    Parameters
    ----------
    to_flatten: Union[MutableMapping, Sequence]
        A dict or sequence to flatten
    sep: str
        The separator to use for keys. Only used when flattening dicts.
    """
    return (
        dict(flatten_dict(to_flatten, sep=sep))
        if isinstance(to_flatten, MutableMapping)
        else list(flatten_list(to_flatten))
    )


class ExtendedQueue(Queue):
    """A variation of :class:`asyncio.Queue` with additional helpful queue management features

    Contains check::

        >>> queue = ExtendedQueue()
        >>> queue.put_nowait('x')
        >>> 'x' in queue
        True

    Iterate through all items like a list::

        >>> queue = ExtendedQueue()
        >>> queue.put_nowait('x')
        >>> for item in queue:
        ...     print(repr(item))
        'x'

    Async iteration::

        >>> queue = ExtendedQueue()
        >>> queue.put_nowait('x')
        >>> async for item in queue:
        ...     print(repr(item))
        'x'

    .. important::
        Async iteration will wait until a new item is added to the queue. As such, this is
        similar to using ``Queue.get`` in a never-returning while loop.

    """

    def __contains__(self, item):
        return item in getattr(self, "_queue")

    def __len__(self):
        return len(getattr(self, "_queue"))

    def __iter__(self):
        while not self.empty():
            yield self.get_nowait()

    async def __aiter__(self):
        while True:
            yield await self.get()


async def alist(gen: AsyncIterable[_T]) -> List[_T]:
    """Convert an async iterable to a list

    This is simply a shortcut method for::

        [x async for x in gen]
    """
    return [i async for i in gen]


@contextmanager
def timer(name: str, *, log: logging.Logger = None):
    """A simple context manager to log how long it took for a task to complete"""
    if log is None:
        from ._internal import log
    t1 = datetime.utcnow()
    try:
        yield
    finally:
        delta = datetime.utcnow() - t1
        log.debug("Task %r took %s ms", name, delta.total_seconds() * 1000)


def chunks(seq: Sequence, chunk_every: int) -> Iterable[Sequence]:
    """Yield successive n-sized chunks from seq

    Original source: https://stackoverflow.com/a/312464
    """
    for i in range(0, len(seq), chunk_every):
        yield seq[i : i + chunk_every]
