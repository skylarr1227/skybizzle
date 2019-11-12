import os
from functools import lru_cache
from pathlib import Path
from typing import Union, List, Callable, Optional, ClassVar

from .locale import Locale
from .util import closest_locale

__all__ = ("LocaleMapping",)


class LocaleMapping:
    #: The file extension to look for when loading locales from disk.
    #: This should start with a period.
    ext: ClassVar[str] = ".toml"

    def __init__(
        self,
        path: Path,
        locales: Union[str, List[str], Callable[[], Union[str, List[str]]]],
        locale_cls=Locale,
    ):
        self.path = path
        self._names = locales
        self._cls = locale_cls
        self._locales = {}

    def __iter__(self):
        for name in self.locales:
            yield self[name]

    def __getitem__(self, name):
        if isinstance(name, (int, slice)):
            return list(self)[name]

        if name not in self._locales:
            name = self.negotiate(name)
            if name is None:
                raise KeyError(name)
            self._locales[name] = self._cls(name=name, path=self.path / (name + self.ext))
        return self._locales[name]

    def __contains__(self, item):
        return item in self.locales

    def __len__(self):
        return len(self._locales)

    def __repr__(self):
        return f"<{type(self).__name__} locales={self.locales!r}>"

    @property
    def names(self) -> List[str]:
        """List[str]: Unaltered list of all configured locale names

        Locale names in this list are not guaranteed to exist on disk.
        """
        locales = self._names
        if callable(locales):
            locales = locales()
        if not isinstance(locales, (list, tuple)):
            locales = [locales]
        return locales

    @names.setter
    def names(self, value):
        self._names = value
        self.negotiate.cache_clear()

    @property
    def locales(self) -> List[str]:
        """List[str]: All configured locale names that exist on disk

        While all locales in this list are guaranteed to exist on disk, they cannot be guaranteed
        to be actually usable or contain any useful strings.
        """
        names = [self.negotiate(x) for x in self.names]
        return list(dict.fromkeys([x for x in names if x]))

    @lru_cache()
    def negotiate(self, name: str) -> Optional[str]:
        return closest_locale(
            name,
            [
                x.replace(self.ext, "")
                for x in os.listdir(str(self.path.resolve()))
                if x.endswith(self.ext)
            ],
        )
