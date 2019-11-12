from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Union, Optional, Callable, Dict, Any

import discord
from babel.dates import format_timedelta
from discord.ext.commands import BadArgument, Converter
from redbot.core.utils.chat_formatting import escape

from .utils import _frange, TIME_QUANTITIES
from .._internal import translate

__all__ = ("FutureTime", "ConfigKey", "BelowMinDuration", "AboveMaxDuration", "NoDuration")
TIME_AMNT_REGEX = re.compile(
    r"(?P<AMOUNT>[0-9]+(?:\.[0-9]+)?)\s?(?P<PERIOD>[a-z]+)?", re.IGNORECASE
)


class BelowMinDuration(ValueError):
    """Raised if an input resolves to be below a converter's minimum required duration"""


class AboveMaxDuration(ValueError):
    """Raised if an input resolves to be above the converter's max allowed duration"""


class NoDuration(ValueError):
    """Raised if an input fails to resolve to any meaningful timedelta"""


class FutureTime(Converter):
    # noinspection PyUnresolvedReferences
    """
    This class contains features originally taken from ZeLarpMaster's v2 Reminders cog,
    with many modifications made from the `original source`_.

    .. _original source: https://github.com/ZeLarpMaster/ZeCogs/blob/53ee681/reminder/reminder.py

    This class can be used as a type hint if you'd like discord.py to handle the work of
    converting an input for you::

        >>> from swift_libs.time import FutureTime
        >>> from redbot.core import commands
        >>> @commands.command()
        ... async def my_cmd(ctx, duration: FutureTime().min_time.seconds(10)):
        ...     # duration will be an instance of datetime.timedelta
        ...     # invalid input for duration will result in a BadArgument exception,
        ...     # which is handled by discord.py like any other conversion failure
        ...     await ctx.send(f"Total seconds: {duration.total_seconds()}")
    """

    def __init__(self, **kwargs):
        self._original_kwargs: Dict[str, Any] = kwargs.copy()
        self._min_time: Optional[float] = kwargs.pop("min_time", None)
        self._max_time: Optional[float] = kwargs.pop("max_time", None)
        self._default_period: Optional[str] = kwargs.pop("default_period", None)
        if kwargs:
            raise TypeError(
                "Got unexpected keyword argument {!r}".format(next(iter(kwargs.keys())))
            )

    def __repr__(self):
        return "{}({})".format(
            type(self).__name__, ", ".join([f"{k}={v!r}" for k, v in self._original_kwargs.items()])
        )

    def from_str(self, duration: str) -> timedelta:
        """Resolve an input duration with the converter's current configuration options

        All exceptions this method raises are subclasses of :class:`ValueError`.

        Raises
        -------
        BelowMinDuration
        AboveMaxDuration
        NoDuration
        """
        duration = self.get_seconds(
            duration, max_seconds=self._max_time, default_period=self._default_period
        )
        if self._min_time and duration < self._min_time:
            raise BelowMinDuration()
        if duration == 0.0:
            raise NoDuration()
        return timedelta(seconds=duration)

    @staticmethod
    def get_seconds(
        duration: str,
        *,
        default_period: Optional[str] = None,
        max_seconds: Union[int, float] = None,
        adjust: bool = True,
    ) -> float:
        """Parse ``duration`` into the corresponding amount of seconds

        If you're looking to use configuration options, you should use :attr:`from_str` instead.

        Example
        -------
        >>> FutureTime.get_seconds("1m")
        60.0
        >>> FutureTime.get_seconds("1.5m")
        90.0
        >>> # you can also set a default period when no time period is given
        >>> # and yes: the normal period parsing works here, so you can pass 'm' instead of 'minute'
        >>> FutureTime.get_seconds("3", default_period="minute")
        180.0
        >>> # you can also combine bare integers with manually set time periods
        >>> # (though, it looks fairly wonky, so you may not want to actually do this)
        >>> FutureTime.get_seconds("2m 3", default_period="hour")
        10920.0
        >>> # float input is also accepted and correctly handled:
        >>> FutureTime.get_seconds("1.5m")
        90.0
        >>> FutureTime.get_seconds("30.4m")
        1818.0

        Parameters
        ----------
        duration: :class:`str`
            The input string to convert into seconds
        default_period: Optional[:class:`str`]
            The default time period that bare integers will be assumed to be in.
            If this is :obj:`None`, bare integers are completely ignored.
        max_seconds: Union[:class:`int`, :class:`float`]
            If the given string resolves to a delta that exceeds this given duration, a
            ValueError will be raised.
        adjust: :class:`bool`
            If this is :obj:`False`, month and year deltas will return a flat 30 and 365 days
            respectively, instead of their default behavior of adapting to the current timedelta
            being parsed to be more friendly to understand.

        Returns
        -------
        :class:`float`
            The amount of seconds parsed from ``duration``

        Raises
        ------
        AboveMaxDuration
        """
        seconds = 0
        for time_match in TIME_AMNT_REGEX.finditer(duration):
            time_amnt = float(time_match.group("AMOUNT"))
            try:
                time_abbrev = time_match.group("PERIOD")
                if time_abbrev is None:
                    raise KeyError()
            except (IndexError, KeyError):
                if not default_period:
                    continue
                time_abbrev = default_period

            time_quantity = discord.utils.find(
                lambda t: t[0].startswith(time_abbrev),  # pylint:disable=cell-var-from-loop
                TIME_QUANTITIES.items(),
            )
            if time_quantity is not None:
                if isinstance(time_quantity[1], Callable):
                    now = datetime.utcnow()
                    for i in _frange(time_amnt):
                        s = time_quantity[1](now + timedelta(seconds=seconds), adjust=adjust)
                        if i < 1:
                            s *= i
                        seconds += s
                else:
                    seconds += time_amnt * time_quantity[1]
            # short circuit if we're over max duration
            if max_seconds and seconds > max_seconds:
                raise AboveMaxDuration()
        return seconds

    async def convert(self, ctx, argument: str) -> timedelta:
        # this doc string is intentionally left empty; use `from_str` instead
        # of directly calling this method.
        """"""
        try:
            return self.from_str(argument)
        except NoDuration:
            raise BadArgument(
                translate(
                    "time.fail_parse_delta",
                    input=escape(argument, mass_mentions=True, formatting=True),
                )
            )
        except BelowMinDuration:
            raise BadArgument(
                translate(
                    "time.min_duration", delta=format_timedelta(timedelta(seconds=self._min_time))
                )
            )
        except AboveMaxDuration:
            raise BadArgument(
                translate(
                    "time.max_duration", delta=format_timedelta(timedelta(seconds=self._max_time))
                )
            )

    ###########

    def strict(self) -> FutureTime:
        """Deprecated method; kept around for backwards compatibility.

        All conversions are now treated strictly and will always raise a :class:`NoDuration`
        or :class:`discord.BadArgument` exception if an input doesn't resolve to anything.
        """
        warnings.warn(
            "FutureTime.strict is deprecated; all conversions are now treated strictly and will"
            " always raise an exception if an input doesn't resolve to anything.",
            DeprecationWarning,
        )
        return self

    @property
    def default_period(self) -> ConfigKey:
        """Configure the converter's default time period"""
        return ConfigKey("default_period", self._original_kwargs)

    @property
    def min_time(self) -> ConfigKey:
        """Configure the converter's minimum time required"""
        return ConfigKey("min_time", self._original_kwargs)

    @property
    def max_time(self) -> ConfigKey:
        """Configure the converter's maximum allowed time"""
        return ConfigKey("max_time", self._original_kwargs)


@dataclass()
class ConfigKey:
    """FutureTime configuration class

    This class is designed to be used to build a configured FutureTime in a fluent-style fashion.

    .. important::
        Months and years add a flat 30 and 365 days respectively to the current setting,
        whereas parsing usually tries for a "as close as possible to what's being asked for"
        approach with parsing input, meaning an input of `1y` may end up being one year and
        a day to account for a leap day.

    Example
    -------
    >>> FutureTime().min_time(seconds=10)
    FutureTime(min_time=10.0)
    >>> FutureTime().min_time.seconds(10)
    FutureTime(min_time=10.0)
    >>> FutureTime().default_period(hours=...)  # the value is ignored for default_period
    FutureTime(default_period='hours')
    >>> FutureTime().default_period.hours()
    FutureTime(default_period='hours')
    """

    key: str
    kwargs: dict

    def __call__(self, *args, **kwargs):
        if self.key == "default_period":
            return self.set(args[0] if args else next(iter(kwargs.keys())))

        value: float = sum((self.kwargs.get(self.key, 0.0), *args))
        for k, v in kwargs.items():
            value += FutureTime.get_seconds(f"{v} {k}", adjust=False)
        return self.set(value)

    def set(self, value) -> FutureTime:
        kwargs = self.kwargs.copy()
        kwargs[self.key] = value
        return FutureTime(**kwargs)

    def seconds(self, seconds: float = None) -> FutureTime:
        """Add X seconds to the current configuration value, or set seconds as the default period"""
        return self(seconds=seconds)

    def minutes(self, minutes: float = None) -> FutureTime:
        """Add X minutes to the current configuration value, or set minutes as the default period"""
        return self(minutes=minutes)

    def hours(self, hours: float = None) -> FutureTime:
        """Add X hours to the current configuration value, or set hours as the default period"""
        return self(hours=hours)

    def days(self, days: float = None) -> FutureTime:
        """Add X days to the current configuration value, or set days as the default period"""
        return self(days=days)

    def weeks(self, weeks: float = None) -> FutureTime:
        """Add X weeks to the current configuration value, or set weeks as the default period"""
        return self(weeks=weeks)

    def months(self, months: float = None) -> FutureTime:
        """Add X months to the current configuration value, or set months as the default period"""
        return self(months=months)

    def years(self, years: float = None) -> FutureTime:
        """Add X years to the current configuration value, or set years as the default period"""
        return self(years=years)
