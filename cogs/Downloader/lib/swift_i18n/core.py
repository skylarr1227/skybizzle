from __future__ import annotations

import warnings
from locale import getlocale
from pathlib import Path
from typing import Union, Dict, Any, Optional, List

from .humanize import Humanize
from .locale import Locale
from .map import LocaleMapping
from .util import LazyStr

__all__ = ("Translator", "TranslatorGroup")


class undefined:
    pass


class Translator:
    """Simple yet intelligent translator

    Example
    -------
    .. code-block:: python

        from swift_i18n import Translator

        # `locales` may also be a single str, or a callable that returns one str
        # or a list of str items
        translate = Translator(__file__, locales=['en-US'])

        # This assumes you have an en-US.toml file in your locales directory containing
        # the following value:
        # hello = 'Hello, {name}'
        translate('hello', name='world')  # -> 'Hello, world'

        # messages = '''
        # You have {count, plural,
        #      =0 {no unread messages}
        #     one {# unread message}
        #   other {# unread messages}
        # }''
        translate('messages', count=0)  # -> 'You have no unread messages'
        translate('messages', count=1)  # -> 'You have 1 unread message'
        translate('messages', count=2)  # -> 'You have 2 unread messages'

    Parameters
    ----------
    path: str
        The current file path for your code; this is usually the value of ``__file__``. This may be
        :obj:`None` if ``mapping`` is already instantiated.

    Keyword Arguments
    -----------------
    locales: Union[str, List[str], Callable[[], Union[str, List[str]]]]
        One or more locales, or a callable to call in order to retrieve currently the set locale(s).
        This defaults to :func:`locale.getlocale`.
    mapping: Optional[Union[LocaleMapping, Type[LocaleMapping]]]
        The locale mapping class to use
    cls: Optional[Type[Locale]]
        Locale class type to use. This is not used if ``mapping`` is passed and is already
        instantiated.
    dir: Optional[str]
        The directory name to descend into from the parent directory of ``path``.
        Defaults to ``locales``.
    base_key: Optional[str]
        Base key to append to translation keys when this translator instance is called
    strict: Optional[bool]
        If this is :obj:`True` and a translation call doesn't resolve to any existing string,
        it will raise a :class:`KeyError` instead of returning the default value.

    Attributes
    ----------
    locales: LocaleMapping
        Iterable read-only mapping of all configured and available locales
    base_keys: List[str]
        List of keys that will be appended to all translations ran through this translator
    strict: bool
        If this is :obj:`True`, this translator will raise a KeyError for invalid translation
        keys instead of a default value.
    """

    def __init__(self, path: Optional[str], **kwargs):
        locale_map = kwargs.pop("mapping", LocaleMapping)
        if isinstance(locale_map, type):
            locale_map = locale_map(
                Path(path).parent / kwargs.pop("dir", "locales"),
                locales=kwargs.pop("locales", lambda: getlocale()[0]),
                locale_cls=kwargs.pop("cls", Locale),
            )
        self.locales: LocaleMapping = locale_map
        self.base_key: str = kwargs.pop("base_key", "")
        self.strict = kwargs.pop("strict", False)

    def __repr__(self):
        return f"<{type(self).__name__} locales={self.locales!r}>"

    def __call__(self, *keys: Union[str, Dict[str, Any]], default: Any = undefined, **kwargs):
        """Retrieve a translated string

        This will attempt to retrieve the requested string in the order that your ``locales``
        are configured in.

        Dicts passed as positional arguments are assumed to be keyword arguments for the purposes
        of formatting the retrieved string.

        Nested keys may be accessed by either separating their key strings when calling
        this translator, or by adding ``.`` to denote a nested key, meaning to access ``a.b``
        you could use either ``translate("a", "b")`` or ``translate("a.b")``.

        .. important::
            If you retrieve a string that expects format arguments and fail to pass them,
            this method will raise a :class:`KeyError`.

        Example
        -------
        .. code-block:: python

            # This assumes you have both a `debug` meta-locale and `en-US` locale in your locales
            # directory.
            translate = Translator(__file__, locales=['debug', 'en-US'])
            # this is available in 'debug', so it's returned from that locale as it's
            # the first configured locale
            translate('hello')  # -> 'debug string'
            # this however may not be available in 'debug', so it's loaded from 'en-US' instead
            translate('example')  # -> 'an example string'
            # this isn't available in either, so the key name is returned instead, in
            # addition to a RuntimeWarning. note that if you initialized your translator with
            # the `strict` kwarg, this will instead raise a KeyError unless you specify
            # a default value for this translation call
            translate('non-existent')  # -> 'non-existent', in addition to a RuntimeWarning
        """
        keys = list(keys)
        for arg in keys.copy():
            if isinstance(arg, dict):
                keys.remove(arg)
                kwargs.update(arg)
        if self.base_key:
            keys.insert(0, self.base_key)
        keys = ".".join(keys)

        translated = undefined
        from_locale: Locale = ...
        for locale in self.locales:
            if keys in locale:
                translated = locale[keys]
                from_locale = locale
                break

        if from_locale is ...:
            if self.strict and default is undefined:
                raise KeyError(keys)
            warnings.warn(f"No string with the ID {keys!r} was found", RuntimeWarning)
            return default if default is not undefined else keys

        if kwargs:
            if isinstance(translated, (str, LazyStr)):
                for k, v in kwargs.items():
                    if isinstance(v, Humanize):
                        kwargs[k] = v(locale=from_locale.babel)
                return translated.format(**kwargs)
            else:
                warnings.warn(
                    f"Format keyword arguments were specified, but key {keys!r} "
                    f"resolved to a non-string",
                    RuntimeWarning,
                )

        if isinstance(translated, LazyStr):
            return str(translated)
        return translated

    @property
    def locale(self) -> Locale:
        """:class:`Locale`: Get the bot's primary locale"""
        return self.locales[0]

    def lazy(self, *keys, **kwargs):
        """Lazily translate a string only when needed

        This method returns a class which attempts to mimic :class:`str` wherever possible.

        Example
        -------
        >>> translate = Translator(__file__)
        >>> translate('hello', name='world')
        'hello world'
        >>> translate.lazy('hello', name='world')
        <LazyStr keys=('hello',) kwargs={'name': 'world'}>
        >>> str(translate.lazy('hello', name='world'))
        'hello world'
        """
        return LazyStr(self, keys, kwargs)

    def group(self, *keys: str, **kwargs) -> TranslatorGroup:
        # noinspection PyTypeChecker
        """Create a new group translator instance

        This works the same as if you simply specified ``base_key`` when creating a new
        Translations class instance.

        A group translator shares all the same locale and loader objects with the root translator.

        Example
        -------
        >>> translate = Translator(__file__)
        >>> sub = translate.group("group")
        >>> sub('hello')
        'hello world'
        """
        base = [*keys]
        if self.base_key:
            base.insert(0, self.base_key)
        return TranslatorGroup(
            path=None,
            parent=self,
            base_key=".".join(base),
            mapping=self.locales,
            strict=kwargs.pop("strict", self.strict),
            **kwargs,
        )


class TranslatorGroup(Translator):
    def __init__(self, *args, **kwargs):
        self.parent: Translator = kwargs.pop("parent")
        super().__init__(*args, **kwargs)

    @property
    def locales(self) -> LocaleMapping:
        return self.root.locales

    @locales.setter
    def locales(self, _):
        pass

    @property
    def root(self) -> Translator:
        p = self.parent
        while hasattr(p, "parent"):
            p = p.parent
        return p

    def generic(self, *args, **kwargs):
        """Get a string from the root translator

        This can be useful if your locale root contains a collection of generic strings
        and use groups for sub-modules.
        """
        # pylint wtf yes this is callable shut the fuck up
        return self.root(*args, **kwargs)  # pylint:disable=not-callable
