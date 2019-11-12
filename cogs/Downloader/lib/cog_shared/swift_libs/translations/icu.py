import logging
from functools import partial
from typing import Union, Sequence

from parsimonious import IncompleteParseError
from pyseeyou import format_tree, ICUMessageFormat

from .locale import Locale
from .utils import LazyStr, parse_unicode
from ..helpers import flatten

__all__ = ("ICULocale",)
log = logging.getLogger("red.swift_libs.translations")


# pylint:disable=super-init-not-called,redefined-builtin
# noinspection PyMissingConstructor,PyShadowingBuiltins
class ICUString(LazyStr):
    __slots__ = ("ast", "locale", "id")

    def __init__(self, locale: str, id: str, ast):
        self.locale = locale
        self.ast = ast
        # Used for debugging and object comparison purposes
        self.id = id

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and other.ast == self.ast
            and other.locale == self.locale
            and other.id == self.id
        )

    def __repr__(self):
        return f"<ICUString locale={self.locale!r} id={self.id!r}>"

    def __call__(self, **kwargs):
        return self.format(**kwargs)

    def __str__(self):
        return self.format()

    def format(self, **kwargs):
        return format_tree(self.ast, kwargs, self.locale)


# pylint:enable=super-init-not-called,redefined-builtin
class ICULocale(Locale):
    """ICU message formatting based locale class

    This locale class overrides string formatting to utilize `pyseeyou`_ instead of
    :attr:`str.format`.

    .. _pyseeyou: https://github.com/rolepoint/pyseeyou

    .. important::
        ICU locales are much more sensitive to mistakes than a standard locale.
        Missing format arguments *will* raise an error, even if you don't specify
        any format arguments.

        Messages that are not properly formatted will fall back to the standard
        :meth:`str.format` syntax.

        Additionally, strings in lists will be returned as :class:`LazyStr` subclass objects. These
        objects attempt to be like strings as much as possible, but have some small nuances -
        namely the fact that they aren't :class:`str` objects. If you need standard string
        objects from lists, the simplest way to get them is by casting them with :class:`str`.

    The ``plurality`` kwarg is ignored when this locale class is used.

    Example
    -------
    >>> from swift_libs.translations import Translations, MemoryLoader, ICULocale
    >>> locale = {
    ...     'nickname': '''`{user}` changed {gender, select,
    ...           male {his}
    ...         female {her}
    ...          other {their}
    ...     } nickname to `{nick}`''',
    ...     'points': '{user} gained {points, plural, one {# point} other {# points}}'
    ... }
    >>> translate = Translations(
    ...     __file__,
    ...     loader=MemoryLoader({'en': locale}),
    ...     locale_type=ICULocale,
    ... )
    >>> translate('nickname', user='odinair#0001', nick='cute gamer girl', gender='female')
    '`odinair#0001` changed her nickname to `cute gamer girl`'
    >>> translate('points_gained', user='odinair#0001', points=1)
    'odinair#0001 gained 1 point'
    >>> translate('points_gained', user='odinair#0001', points=10)
    'odinair#0001 gained 10 points'
    """

    __slots__ = ()

    def _replace(self, k: str, s: Union[str, list]) -> Union[str, ICUString, Sequence]:
        from ..helpers import replace_list_values

        if isinstance(s, dict):
            return self._from_dict(s, k)
        elif isinstance(s, list):
            return replace_list_values(s, converter=partial(self._replace, f"{k}.<list>"))

        try:
            ast = ICUMessageFormat.parse(s)
        except IncompleteParseError:
            log.exception("Failed to parse message %r in locale %s", k, self)
            return s
        else:
            return ICUString(self.name, k, ast)

    def _from_dict(self, d: dict, base: str = None) -> dict:
        nd = {}
        for k, v in d.items():
            full = ".".join([base, k]) if base else k
            if isinstance(v, dict):
                nd[k] = self._from_dict(v)
            else:
                nd[k] = self._replace(full, v)
        return nd

    def load(self):
        # While we *could* override Locale.format or Locale.get instead of replacing str objects
        # with a LazyStr subclass on load, this more readily allows developers and translators
        # to notice incorrect strings when loading locales, instead of when a string is retrieved.
        strs = parse_unicode(flatten(self.loader.load(self.name)))
        log.debug("Parsing AST for %s strings", len(strs))
        return self._from_dict(strs)

    def plurality(self, n: Union[int, float]):
        raise RuntimeError("Plurality is unsupported with ICULocale.")
