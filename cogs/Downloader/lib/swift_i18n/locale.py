from locale import getlocale
import warnings
from pathlib import Path
from typing import Union, Sequence

import toml
from parsimonious import IncompleteParseError, VisitationError
from pyseeyou import ICUMessageFormat, format_tree
from babel import Locale as _BabelLocale, UnknownLocaleError

from .util import flatten_dict, parse_unicode, LazyStr, log

__all__ = ("Locale", "ICUString")


class ICUString(LazyStr):
    # noinspection PyMissingConstructor
    def __init__(self, locale: str, ast):  # pylint:disable=super-init-not-called
        self._locale = locale
        self._ast = ast

    def __repr__(self):
        return f"<ICUString locale={self._locale!r} ast={self._ast!r}>"

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            # pylint:disable=protected-access
            and other._ast == self._ast
            and other._locale == self._locale
            # pylint:enable=protected-access
        )

    def __call__(self, **kwargs):
        return self.format(**kwargs)

    def __str__(self):
        return self.format()

    def format(self, **kwargs):
        try:
            return format_tree(self._ast, kwargs, self._locale)
        except VisitationError as e:
            if e.__context__ and isinstance(e.__context__, KeyError):
                raise e.__context__ from None
            raise


class Locale:
    """Read-only mapping containing strings used for translations"""

    def __init__(self, name: str, path: Path):
        self.name = name
        self._path = path
        self._strs = ...

    def __getitem__(self, item):
        return self.strs[item]

    def __contains__(self, item):
        return item in self.strs

    def __len__(self):
        return len(self.strs)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<{type(self).__name__} strings={len(self)}>"

    @property
    def babel(self) -> str:
        """str: Babel-compatible name for the current locale"""
        try:
            return str(_BabelLocale.parse(str(self).replace("-", "_")))
        except UnknownLocaleError:
            warnings.warn(
                f"Locale {self.name!r} is not known to Babel; falling back to system locale.",
                RuntimeWarning,
            )
            return getlocale()[0]

    @property
    def strs(self) -> dict:
        """dict: All strings available in this locale"""
        if self._strs is ...:
            self.load()
        return self._strs

    def _replace(self, k: str, s: Union[str, list]) -> Union[str, ICUString, Sequence]:
        from .util import replace_list_values

        if isinstance(s, dict):
            return self._from_dict(s, k)
        elif isinstance(s, list):
            index = 0

            def replace(val):
                nonlocal index
                key = f"{k}[{index}]"
                index += 1
                return self._replace(key, val)

            return replace_list_values(s, converter=replace)

        try:
            log.debug("Parsing string %r", k)
            ast = ICUMessageFormat.parse(s)
        except IncompleteParseError:
            log.exception(
                "Failed to parse message %r in locale %s - falling back to"
                " Python string formatting",
                k,
                self,
            )
            return s
        else:
            return ICUString(self.name, ast)

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
        """Load strings for the current locale from disk

        In most cases, you shouldn't need to use this as :attr:`strs` automatically
        calls this method on the first access.
        """
        path = str(self._path.resolve())
        log.debug("Loading locale %r", path)
        with open(path) as f:
            strs = parse_unicode(dict(flatten_dict(toml.load(f))))
        self._strs = self._from_dict(strs)
