import logging
import warnings
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import MutableMapping, Optional, Dict, Union

import yaml
from babel.plural import PluralRule
from redbot.core.i18n import get_locale

from .loader import Loader
from .utils import cleanup_locale, closest_locale, LazyStr
from ..consts import undefined
from ..helpers import TimeCache, flatten

__all__ = ("Locale",)
log = logging.getLogger("red.swift_libs.translations")
_plural_cache: MutableMapping[str, Union[Dict, PluralRule]] = TimeCache(ttl=timedelta(hours=3))


class Locale:
    """A locale containing a key-value mapping of strings for use in translation"""

    __slots__ = ("name", "loader", "_strs")

    def __init__(self, name: str, loader: Loader):
        self.name = name
        self.loader = loader
        self._strs: Optional[Dict[str, str]] = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return (
            f"<{type(self).__name__} name={self.name!r} loader={self.loader!r}"
            f" string_count={len(self.strs)}>"
        )

    def __contains__(self, item):
        return item in self.strs and self.strs[item] is not undefined

    def __getitem__(self, item):
        return self.strs[item]

    @property
    def strs(self) -> Dict[str, str]:
        if self._strs is None:
            log.debug("Loading strings for locale %s with loader %r", self, self.loader)
            self._strs = self.load()
            log.debug("Locale %s loaded", self)
        return self._strs

    def get(self, key: str, default=None):
        return self.strs.get(key, default)

    def load(self) -> Dict[str, str]:
        log.debug("Loading strings for locale %s with loader %r", self, self.loader)
        return flatten(cleanup_locale(self.loader.load(self.name)))

    def format(self, key: str, **kwargs):
        item = self.get(key)
        if not isinstance(item, (str, LazyStr)):
            if kwargs:
                warnings.warn(
                    f"Keyword arguments were specified but the resolved item for translation"
                    f" ID {key!r} in locale {self.name!r} is not a string",
                    UserWarning,
                )
            return item
        return item.format(**kwargs) if kwargs else str(item)

    def plurality(self, n: Union[int, float]):
        warnings.warn(
            "Locale.plurality is deprecated and will be removed in the future. You should"
            " switch to ICULocale if you require plurality handling.",
            DeprecationWarning,
            stacklevel=3,
        )

        locale = self.babel(self.name)
        if locale not in _plural_cache:
            if "plural_rules" not in _plural_cache:
                with open(Path(__file__).parent.parent / "data" / "plurals.yml") as f:
                    # the warning from yaml.load doesn't apply here
                    with warnings.catch_warnings(record=True):
                        _plural_cache["plural_rules"] = yaml.safe_load(f)
            rules = _plural_cache["plural_rules"]
            _plural_cache[locale] = PluralRule(
                rules.get(closest_locale(locale, rules.keys()) or "en")
            )

        return _plural_cache[locale](n)

    # This should be kept around even after plurality is removed, otherwise things *will* break
    @staticmethod
    @lru_cache()
    def babel(locale: str = None) -> str:
        """Get the bot's current locale in a format usable by Babel"""
        from babel import UnknownLocaleError, Locale as bLocale

        bot_locale = (locale or get_locale()).replace("-", "_")
        try:
            return str(bLocale.parse(bot_locale))
        except (UnknownLocaleError, ValueError):
            if bot_locale != get_locale().replace("-", "_"):
                return bot_locale

            warnings.warn(
                f"Bot locale {bot_locale} is not recognized by Babel; falling back to en_US.",
                RuntimeWarning,
            )
            return "en_US"
