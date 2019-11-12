import re
import unicodedata
from inspect import cleandoc
from typing import Optional, List, Tuple, Dict, Union, Iterable, Sequence, Any, Callable

from ..helpers import replace_list_values, flatten

__all__ = ("closest_locale", "parse_unicode", "escape_linebrs", "cleanup_locale", "LazyStr")
unicode_regx = re.compile(r"(?:\\N|\x85){(?P<NAME>[A-Z -]+)}")
linebr = re.compile(r" ?\\\n[ ]*")


class LazyStr:
    """Lazy translation string retrieved from :class:`Translations`.

    This class attempts to mimic :class:`str` as closely as possible, and as such can usually
    be used as a stand-in for a :class:`str` wherever required for translations.

    .. seealso::
        * :func:`Translations.lazy`
    """

    __slots__ = ("translator", "keys", "kwargs")

    def __init__(self, translator: Callable[..., str], keys: Sequence[str], kwargs: Dict[str, Any]):
        self.translator = translator
        self.keys = keys
        self.kwargs = kwargs

    def __eq__(self, other):
        if not isinstance(other, str):
            return False
        return str(self) == other

    def __repr__(self):
        return f"<{type(self).__name__} keys={self.keys!r} kwargs={self.kwargs!r}>"

    def __str__(self):
        return self()

    def __call__(self, **kwargs):
        return self.translator(*self.keys, **self.kwargs, **kwargs)

    def __hash__(self):
        return hash(".".join(self.keys))

    def __getattr__(self, item):
        return getattr(str(self), item)


for _k in dir(str):
    if not (_k.startswith("__") and _k.endswith("__")) or hasattr(LazyStr, _k):
        continue
    # This lambda wrapper fixes `k` being the last item of `dir(str)`, which isn't
    # what we want to happen here.
    (lambda k_: setattr(LazyStr, k_, lambda s, *a, **kw: getattr(str(s), k_)(*a, **kw)))(_k)


def _clean(item: Union[list, str]):
    if isinstance(item, str):
        return cleandoc(escape_linebrs(item))
    elif isinstance(item, list):
        return [_clean(x) for x in item]
    else:
        return item


def cleanup_locale(locale: dict) -> dict:
    """Cleanup locale strings for use

    This runs the given locale dict through :func:`swift_libs.helpers.flatten`
    and it's string values through :func:`inspect.cleandoc`, :func:`escape_linebrs`,
    and :func:`parse_unicode`.
    """
    locale = parse_unicode(flatten(locale))
    for k, v in locale.items():
        locale[k] = _clean(v)
    return locale


def escape_linebrs(text: str) -> str:
    r"""Handle escaped line breaks

    Example
    --------
    >>> mystr = r'''hello \
    ... world'''
    >>> mystr
    'hello \\\nworld'
    >>> escape_linebrs(mystr)
    'hello world'
    """
    return linebr.sub(" ", text).strip()


def closest_locale(
    locale: str,
    available: Iterable[str],
    separator: str = "-",
    replace_with_separator: Iterable[str] = None,
    default: Any = None,
) -> Optional[str]:
    """Match a given locale to a known locale on disk on a close-enough basis"""
    if replace_with_separator is None:
        replace_with_separator = ["_"]

    # [(check against, original), ...]
    available: List[Tuple[str, str]] = [(x, x) for x in available]

    for replace in replace_with_separator:
        locale = locale.replace(replace, separator)
        available = [(x.replace(replace, separator), y) for x, y in available]

    locale = locale.lower()
    available = [(x.lower(), y) for x, y in available]

    try:
        # try to find an exact match before anything else
        return next(unmodified for straw, unmodified in available if straw == locale)
    except StopIteration:
        # if there are no exact matches, fall back to trying to match just the language code,
        # ignoring the region entirely, such as matching `en-GB` to `en-US`
        return next(
            (
                unmodified
                for straw, unmodified in available
                if straw.split(separator)[0] == locale.split(separator)[0]
            ),
            default,
        )


def _parse_unicode(line: str) -> str:
    if not isinstance(line, str):
        return line

    chars = {(x.group(0), x.group("NAME")) for x in unicode_regx.finditer(line)}
    for orig, char in chars:
        line = line.replace(orig, unicodedata.lookup(char))
    return line


def parse_unicode(data: Dict[str, Union[str, dict, list]]) -> dict:
    """Parse all named unicode character escape sequences in dict values

    Parameters
    ----------
    data: Dict[:class:`str`, Union[str, List[str], Dict[str, ...]]]
        The dict to parse string values for. It's expected that all values are some kind of string,
        be it a normal string, lists of strings, or a dict containing string-like values.

    Returns
    -------
    :class:`dict`
        The dict with parsed values

    Raises
    ------
    ValueError
        Raised if a value has an invalid named unicode escape sequence
    """

    for k, v in data.items():
        try:
            if isinstance(v, dict):
                v = parse_unicode(v)
            elif isinstance(v, str):
                v = _parse_unicode(v)
            elif isinstance(v, list):
                v = list(replace_list_values(v, converter=_parse_unicode))
        except KeyError as e:
            raise ValueError(*e.args) from e

        data[k] = v

    return data
