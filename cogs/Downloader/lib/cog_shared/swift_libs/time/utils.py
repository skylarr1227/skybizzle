from collections import OrderedDict
from datetime import datetime, timedelta
from math import floor
from typing import MutableMapping, Union, Callable, Optional

# Almost all of the following code assumes that we're using the Gregorian calendar,
# and will very likely throw up everywhere if that assumption is rendered false.
# If you've come here to fix exactly that; good luck. You're going to need it.


def is_leap_year(year):
    # if the year is evenly divisible by 4
    if year % 4 == 0:
        # except if it's divisible by 100
        if year % 100 == 0:
            # unless it's also divisible by 400
            if year % 400 == 0:
                return True
            return False
        return True
    return False


def get_max_days(year: int = None):
    if year is None:
        year = datetime.utcnow().year
    return {
        # Jan
        1: 31,
        # Feb
        2: 28 if not is_leap_year(year) else 29,
        # Mar
        3: 31,
        # Apr
        4: 30,
        # May
        5: 31,
        # Jun
        6: 30,
        # Jul
        7: 31,
        # Aug
        8: 31,
        # Sep
        9: 30,
        # Oct
        10: 31,
        # Nov
        11: 30,
        # Dec
        12: 31,
    }


def _frange(x, y=None, step=1):
    if y is None:
        x, y = 1, x + 1
    # this will cause some floating point rounding problems, but it's insignificant enough for our
    # use case that I just don't consider it to be an issue worth taking the time to fix.
    dec = y % 1
    yield from range(x, floor(y), step)
    if dec:
        yield dec


def _month_delta(now=None, adjust: bool = True) -> float:
    if adjust is False:
        return timedelta(days=30).total_seconds()

    if now is None:
        now = datetime.utcnow()

    if now.month == 12:
        month = 1
        year = now.year + 1
        # we don't have to do any day-related checks on dec -> jan, since both are 31 days long
        day = now.day
    else:
        month = now.month + 1
        year = now.year
        # this is probably the best that can be done here without making some weird assumptions
        # or just adding a flat 30-31 days
        day = min(now.day, get_max_days()[now.month + 1])

    return (now.replace(day=day, month=month, year=year) - now).total_seconds()


def _year_delta(now=None, adjust: bool = True) -> float:
    if adjust is False:
        return timedelta(days=365).total_seconds()

    if now is None:
        now = datetime.utcnow()
    return (
        now.replace(year=now.year + 1, day=min(now.day, get_max_days(now.year + 1)[now.month]))
        - now
    ).total_seconds()


TIME_QUANTITIES: MutableMapping[
    str, Union[float, Callable[[Optional[datetime]], float]]
] = OrderedDict(
    [
        ("seconds", 1.0),
        ("minutes", 60.0),
        ("hours", 60.0 * 60.0),
        ("days", 60.0 * 60.0 * 24.0),
        ("weeks", 60.0 * 60.0 * 24.0 * 7.0),
        ("months", _month_delta),
        ("years", _year_delta),
    ]
)
