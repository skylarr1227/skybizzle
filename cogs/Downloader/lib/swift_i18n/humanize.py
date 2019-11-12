import datetime
from functools import singledispatch

from babel.dates import format_timedelta, format_datetime, format_date, format_time
from babel.lists import format_list
from babel.numbers import format_decimal

__all__ = ("Humanize",)


# noinspection PyUnusedLocal
@singledispatch
def humanize(val, args, kwargs):  # pylint:disable=unused-argument
    raise TypeError(f"{type(val).__name__!r} is not a recognized type")


@humanize.register(datetime.timedelta)
def _timedelta(delta, args, kwargs):
    return format_timedelta(delta, *args, **kwargs)


@humanize.register(datetime.datetime)
def _datetime(dt, args, kwargs):
    return format_datetime(dt, *args, **kwargs)


@humanize.register(datetime.date)
def _date(date, args, kwargs):
    return format_date(date, *args, **kwargs)


@humanize.register(datetime.time)
def _time(time, args, kwargs):
    return format_time(time, *args, **kwargs)


@humanize.register(list)
@humanize.register(set)
@humanize.register(tuple)
def _sequence(seq, args, kwargs):
    # Sets aren't sequences, so we have to specifically cast them to lists.
    return format_list(list(seq), *args, **kwargs)


@humanize.register(int)
@humanize.register(float)
def _decimal(num, args, kwargs):
    return format_decimal(num, *args, **kwargs)


@humanize.register(type(_decimal))
def _callable(cb, args, kwargs):
    return cb(*args, **kwargs)


class Humanize:
    # noinspection PyUnresolvedReferences
    """Special placeholder class for use in translations

    Format argument values with this class type are special-cased by :class:`Translator`,
    and will instead be rendered in the output string with the formatted value for the locale
    the returned string originated from.

    This allows for more complex translation setups where you can't always be sure if you're
    loading strings from just one locale, such as with context-dependent locales.

    The following value types are supported and will be ran through their respective `Babel`_
    format functions:

    * :class:`datetime.datetime`
    * :class:`datetime.date`
    * :class:`datetime.time`
    * :class:`datetime.timedelta`
    * :class:`list`
    * :class:`set`
    * :class:`tuple`
    * :class:`int`
    * :class:`float`

    A function which accepts any arguments, including a ``locale`` keyword argument,
    may also be used.

    Use of any other types will result in a :class:`TypeError` being raised.

    .. _Babel: http://babel.pocoo.org/en/latest/

    Example
    --------
    >>> from swift_i18n import Translator, Humanize
    >>> from datetime import datetime
    >>> translate = Translator(__file__)
    >>> dt = datetime.now()
    >>> translate('today', date=Humanize(dt.date()), time=Humanize(dt.time()))
    "Today is Aug 27, 2019, and the time is currently 1:33:20 PM"
    """

    def __init__(self, value, *args, **kwargs):
        self.value = value
        self.args = args
        self.kwargs = kwargs
        # Fail early if the given value is an unrecognized type
        if type(value) not in humanize.registry:
            raise TypeError(f"Unexpected type: {type(value).__qualname__!r}")

    def __str__(self):
        return self()

    def __call__(self, *args, **kwargs):
        return humanize(self.value, self.args, {**self.kwargs, **kwargs})
