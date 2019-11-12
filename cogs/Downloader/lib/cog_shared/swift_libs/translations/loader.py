import os
import warnings
from functools import lru_cache
from pathlib import Path
from typing import ClassVar, List, Dict, Any, Optional

import toml
import yaml

from .utils import closest_locale

__all__ = ("Loader", "MemoryLoader", "TOMLLoader")


class Loader:
    """Generic locale loader class

    This loads .yml files by default, but can be modified by subclassing this.

    .. admonition:: Example JSON Loader

        >>> class MyLoader(Loader):
        ...     # this is the file extension the loader will use to recognize available locales
        ...     ext = "json"
        ...     def load(self, locale: str) -> dict:
        ...         pass  # batteries not included
        ...         # you should make use of the cache available with self._cache[locale]
    """

    ext: ClassVar[str] = "yml"

    def __init__(self, path: Path):
        self.path = path
        self._known_locales = None
        self._cache = {}

    def __repr__(self):
        return f"<{type(self).__name__} path={str(self.path)!r}>"

    def available_locales(self) -> List[str]:
        """Get a list of all locales this loader can load on disk

        Locales in the returned list may or may not actually be loadable.
        """
        if self._known_locales is None:
            ext = f".{self.ext}"
            self._known_locales = [
                x.replace(ext, "") for x in os.listdir(str(self.path.resolve())) if x.endswith(ext)
            ]
        return self._known_locales

    @lru_cache()
    def negotiate(self, locale: str, default: Any = None) -> Optional[str]:
        """Find the closest matching locale available on disk for the given locale name

        .. seealso::
            * :func:`swift_libs.translations.utils.closest_locale`

        Parameters
        ----------
        locale: str
            The locale to attempt to find the closest match for on disk
        default: Any
            The default value to return if the given locale does not exist on disk
        """
        return closest_locale(locale, self.available_locales(), default=default)

    def load(self, locale: str) -> dict:
        """Load the given locale from disk, or from cache if it was previously loaded

        The returned locale is as-is from disk with no modifications made.
        """
        if locale not in self._cache:
            with open(str(self.path / f"{locale}.{self.ext}")) as f:
                # this is a safe use of yaml, so the warning emitted by red doesn't apply here.
                with warnings.catch_warnings(record=True):
                    self._cache[locale] = yaml.safe_load(f) or {}
        return self._cache[locale]

    def dump(self):
        """Dump the loader cache

        Locales keep their own separate cache, so clearing just the loader cache is not enough to
        retrieve new translated strings from disk. You should use
        :attr:`swift_libs.translations.translator.LocaleProxy.dump` if that's what you're after.
        """
        self._known_locales = None
        self._cache = {}
        self.negotiate.cache_clear()


class MemoryLoader(Loader):
    """Memory-based locale loader

    This simply returns locales specified on setup, and as such this is really only useful
    for debugging purposes.

    Example
    -------
    >>> from swift_libs.translations import Translations, MemoryLoader
    >>> translate = Translations(__file__, loader=MemoryLoader({'en-US': {'hello': 'hello world'}}))
    >>> translate('hello')
    'hello world'
    """

    ext = "memory"

    # noinspection PyMissingConstructor
    def __init__(self, locales: Dict[str, Dict[str, Any]]):  # pylint:disable=super-init-not-called
        self.path = None
        # we're abusing the fact that we cache everything we can here to avoid having to override
        # any methods beyond __init__ and dump
        self.locales = locales

    def __repr__(self):
        return f"<MemoryLoader locales={self._known_locales}>"

    @property
    def locales(self) -> Dict[str, dict]:
        return self._cache

    @locales.setter
    def locales(self, value: Dict[str, dict]):
        self._cache = value
        self._known_locales = list(value.keys())

    def dump(self):
        """No-op method"""
        pass


class TOMLLoader(Loader):
    """TOML-based loader"""

    ext = "toml"

    def load(self, locale: str) -> dict:
        if locale not in self._cache:
            with open(str(self.path / f"{locale}.{self.ext}")) as f:
                self._cache[locale] = toml.load(f) or {}
        return self._cache[locale]
