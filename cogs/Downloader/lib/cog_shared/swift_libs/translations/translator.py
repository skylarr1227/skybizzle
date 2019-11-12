from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import Dict, Union, Any, Type, Callable, Optional, Iterator, Tuple

from discord.ext.commands import Cog, Command
from redbot.core.i18n import get_locale
from redbot.core.utils import deduplicate_iterables

from .loader import Loader
from .locale import Locale
from .utils import closest_locale, LazyStr
from ..consts import undefined

__all__ = ("Translations",)
log = logging.getLogger("red.swift_libs.translations")


class LocaleProxy:
    """Locale cache proxy class

    This class can be used somewhat like a read-only list with additional dict-like key access.

    Example
    -------
    >>> translate = Translations(__file__)
    >>> translate.locales
    <LocaleProxy default='en-US' loader=<Loader path='.../locales'> cls=<class 'Locale'>>
    >>> translate.locales['en-US']
    <Locale name='en-US' loader=<Loader path='.../locales'> string_count=...>
    >>> translate.locales[-1]
    <Locale name='en-US' loader=<Loader path='.../locales'> string_count=...>
    """

    __slots__ = ("loader", "default", "locale_type", "_locales")

    def __init__(self, loader: Loader, default: str = "en-US", locale_type: Type[Locale] = Locale):
        self.loader = loader
        self.default = default
        self.locale_type: Type[Locale] = locale_type
        self._locales: Dict[str, Locale] = {}

    def __repr__(self):
        return (
            f"<LocaleProxy default={self.default!r} loader={self.loader!r}"
            f" locale_type={self.locale_type!r}>"
        )

    def __getitem__(self, locale: Union[str, int, slice]) -> Locale:
        if isinstance(locale, (int, slice)):
            return list(self)[locale]
        if not isinstance(locale, str):
            raise TypeError(f"Expected type str, int, or slice, got {type(locale).__name__}")
        name = self.loader.negotiate(locale)
        if name is None:
            raise KeyError(locale)
        if name not in self._locales:
            self._locales[name] = self.locale_type(name=name, loader=self.loader)
        return self._locales[name]

    def __contains__(self, item):
        if not isinstance(item, str):
            return False
        return self.loader.negotiate(item) is not None

    def __iter__(self) -> Iterator[Locale]:
        return (self[x] for x in self.names)

    def __len__(self):
        return len(self.names)

    @property
    def bot(self) -> Tuple[str, ...]:
        """Tuple containing the names of all locales the bot is currently configured to load from

        The returned locales have not been modified from what is configured in Red,
        and as such they may or may not actually exist as usable locales on disk.

        The returned tuple may contain duplicates.

        You should use :attr:`LocaleProxy.names` if you want a list of actually usable locale names.

        Currently, this simply returns the return value of ``get_locale()`` in a tuple,
        but is provided as basic foundational work for handling future per-user/guild locales
        if and when it's implemented in Red.
        """
        # If/when multi-locale support in Red lands, this is roughly how we want to
        # prioritize configured locales to load and retrieve strings from:
        #   1. User
        #   2. Channel
        #   3. Guild
        #   4. Global
        #   5. Default translator locale

        # noinspection PyRedundantParentheses
        return (get_locale(),)

    @property
    def names(self) -> Tuple[str, ...]:
        """Tuple containing the names of all usable locales the bot is configured to load from

        Locales in this tuple are matched from the return value of :attr:`LocaleProxy.bot`
        to the closest available on disk, and as such are guaranteed to exist on disk,
        but cannot be guaranteed to be actually loadable or contain any useful strings.

        The returned tuple is guaranteed to be free of duplicates.
        """
        available = self.loader.available_locales()
        return tuple(
            x
            for x in deduplicate_iterables(
                [closest_locale(x, available, default=None) for x in (*self.bot, self.default)]
            )
            if x is not None
        )

    def dump(self):
        """Dump the locale cache, forcing the next translation to load strings fresh from disk"""
        self._locales = {}
        self.loader.dump()


# noinspection PyShadowingNames
class Translations:
    """A fairly flexible, yet simple and opinionated translator

    Example
    -------

    >>> from swift_libs.translations import Translations
    >>> translate = Translations(__file__)
    >>> translate("example")
    'hello, world!'

    Parameters
    ----------
    path: :obj:`str`
        The current file path, usually the value of ``__file__``. This is used to resolve
        ``locale_dir`` from the parent of the given path. This is allowed to be :obj:`None`
        if either ``loader`` or ``proxy`` is already instantiated.

    Keyword Arguments
    -----------------
    default: :class:`str`
        The default locale to try to resolve; defaults to ``en-US``. This locale will always
        be used as a fallback if the bot's configured locales don't contain a
        requested string.
    dir: :class:`str`
        The directory name in which your locales are stored; defaults to ``locales``.
        Also aliased to ``locale_dir`` for backwards compatibility.
    base_key: Optional[:class:`str`]
        An optional root translation key
    strict: bool
        If this is :obj:`True`, missing translation keys will instead raise a :class:`KeyError`
        instead of returning a placeholder string.
    loader: Union[Loader, Type[Loader]]
        The loader class to use when retrieving locales from disk
    locale: Type[Locale]
        The locale class type to use for loaded locales. Also aliased to ``locale_type`` for
        backwards compatibility.
    proxy: Union[LocaleProxy, Type[LocaleProxy]]
        The locale proxy class to use

    Attributes
    ----------
    locales: LocaleProxy
        The locale proxy used to retrieve locales from disk, or memory if they've been
        previously loaded
    strict: bool
        If this is :obj:`True`, attempted translations that don't match any known translation
        string ID will raise a :class:`KeyError` instead of returning the given translation ID
        with a warning.
    base_key: Optional[str]
        Optional base key to append to all translation string IDs; used by :attr:`group`.
    """

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        path: Optional[str],
        *,
        default: str = "en-US",
        dir: str = "locales",  # pylint:disable=redefined-builtin
        base_key: str = None,
        strict: bool = False,
        loader: Union[Loader, Type[Loader]] = Loader,
        locale: Type[Locale] = Locale,
        proxy: Union[LocaleProxy, Type[LocaleProxy]] = LocaleProxy,
        **kwargs,
    ):
        if "locale_dir" in kwargs:
            warnings.warn(
                "`locale_dir` is a deprecated keyword argument; use `dir` instead",
                DeprecationWarning,
            )
            dir = kwargs.pop("locale_dir")
        if "locale_type" in kwargs:
            warnings.warn(
                "`locale_type` is a deprecated keyword argument; use `locale` instead",
                DeprecationWarning,
            )
            locale = kwargs.pop("locale_type")
        if kwargs:
            raise TypeError(f"Unexpected keyword argument {next(iter(kwargs.keys()))!r}")

        self.base_key = base_key
        self.strict = strict

        if isinstance(loader, type) and isinstance(proxy, type):
            if path is None:
                raise TypeError("path is None, but the given loader is not yet instantiated")
            path = Path(path).parent / dir
            loader = loader(path)

        if isinstance(proxy, type):
            self.locales = proxy(loader=loader, locale_type=locale, default=default)
        else:
            self.locales = proxy

    def __repr__(self):
        return f"<{type(self).__name__} locales={self.locales!r}>"

    def __contains__(self, item):
        if self.base_key:
            item = ".".join([self.base_key, item])
        return any(x for x in self.locales if item in x)

    @property
    def locale(self) -> Locale:
        """:class:`Locale`: Get the bot's primary locale"""
        return self.locales[0]

    @property
    def babel(self) -> str:
        """:class:`str`: Get the current locale in a Babel-usable locale name"""
        return self.locale.babel(self.locale.name)

    def _partial(self, *keys, **kwargs):
        return lambda *_, **__: self(*keys, **kwargs)

    def command(self, *keys: str, **kwargs) -> Callable:
        # noinspection PyUnresolvedReferences
        """Decorator to replace command help doc strings with translated strings

        All regular call arguments able to be passed to :class:`Translations` objects may be used
        here.

        .. important::
            If this is placed below your command decorator, you must use either
            :attr:`cog` or :attr:`attach_to_commands` afterwards on your cog class.

        In most cases, use of this is effectively comparable to::

            >>> @commands.command(i18n=translate)
            ... async def my_command(ctx):
            ...     '''help.my_command'''
            ...     # ... do stuff
        """

        if not any(x for x in keys if isinstance(x, str)):
            raise TypeError("Expected at least one translation key, got none")

        # noinspection PyProtectedMember
        def wrapper(cmd: Union[Command, Callable]):
            if isinstance(cmd, Command):
                # pylint:disable=protected-access
                translator = self._partial(*keys, **kwargs)
                cmd.translator = translator
                # we're accessing _callback because in some cases using the callback property
                # may be undesirable, namely with MiscTools where we use callback wrappers
                # to be able to modify the self property from the MiscTools class to
                # the toolset class a command is actually contained in
                cmd._callback.__doc__ = ".".join(keys)
                if hasattr(cmd, "__original_kwargs__"):
                    cmd.__original_kwargs__["i18n"] = translator
                cmd._help_override = None
                # pylint:enable=protected-access
            elif isinstance(cmd, Callable):
                cmd.__translator__ = self._partial(*keys, **kwargs)
                cmd.__doc__ = ".".join(keys)
            else:
                raise TypeError(f"Expected either Command or Callable, got {type(cmd).__name__}")
            return cmd

        return wrapper

    # noinspection PyProtectedMember
    def attach_to_commands(self, cls: type) -> type:
        """Attach this translator to commands in the given class

        Using this method directly should really only prove to be useful if you're using an
        unconventional setup for a cog, or if you don't want your cog's help documentation
        to be ran through Translations.

        This method may also be used as a decorator in place of :attr:`cog`::

            >>> translate = Translations(__file__)
            >>> @translate.attach_to_commands
            ... class MyCog:
            ...     ...
        """
        for cmd in cls.__dict__.values():
            # pylint:disable=protected-access
            if not isinstance(cmd, Command):
                continue
            if cmd.translator:
                continue

            if cmd._help_override:
                if not isinstance(cmd._help_override, LazyStr):
                    continue
                warnings.warn(
                    f"Command {cmd.qualified_name!r} from class {cls!r} is using a LazyStr"
                    f" object for help documentation. This is strongly discouraged, as"
                    f" this breaks the default discord.py help formatter.",
                    UserWarning,
                )
                override = cmd._help_override
                cmd._help_override = None
                if hasattr(cmd, "__original_kwargs__"):
                    cmd.__original_kwargs__.pop("help", None)
                    cmd.__original_kwargs__.pop("help_override", None)
                self.command(*override.keys, **override.kwargs)(cmd)
                continue

            if hasattr(cmd._callback, "__translator__"):
                translator = cmd._callback.__translator__
                cmd.translator = translator
                if hasattr(cmd, "__original_kwargs__"):
                    # quick and dirty workaround - red doesn't copy translators when commands
                    # are copied, leading to ourselves not being added as the command
                    # translator on versions 3.1.0 through 3.1.2. this was mostly fixed
                    # in 3.1.3, but doesn't entirely fix the issue with commands in classes that
                    # don't have a `__translator__` property, such as with toolsets in MiscTools.
                    cmd.__original_kwargs__["i18n"] = translator
            # pylint:enable=protected-access
        return cls

    def cog(self, tid: str) -> Callable[[Type[Cog]], Type[Cog]]:
        # noinspection PyUnresolvedReferences
        """Translate a cog's help docs and attach this translator to contained commands

        .. note:: This method replaces the ``help`` :class:`property` in your cog class.

        Example
        -------
        >>> translate = Translations(__file__)
        >>> @translate.cog("help.cog_class")
        ... class MyCog(commands.Cog):
        ...     pass  # do stuff

        >>> def setup(bot):
        ...     # ...
        ...     bot.add_cog(MyCog())
        ...     # ...

        Parameters
        ----------
        tid: :class:`str`
            The cog's help string key in your locale files
        """

        def wrapper(cls: Type[Cog]):
            log.debug("Attaching translator for cog class %r", cls)
            self.attach_to_commands(cls)
            cls.__translator__ = self
            cls.help = property(lambda s: s.__translator__(tid))
            return cls

        return wrapper

    def __call__(
        self,
        *keys: Union[str, dict],
        default: Any = undefined,
        plurality: Union[int, float, str] = None,
        **kwargs,
    ) -> str:
        """Get a translated string

        .. note::
            Passing either ``"key1", "key2"`` or ``"key1.key2"`` to this is effectively
            the same as using ``["key1"]["key2"]`` to access dict values.

        Arbitrary keyword arguments can be given to format the resolved string before it's returned.

        If dicts are passed as positional arguments, their items are treated as kwargs
        for the purposes of translations.

        Example
        -------
        >>> translate = Translations(__file__)
        >>> translate("nested", "translation", "key")
        'hello from my nested translation key'
        >>> translate("nested.translation.key")
        'hello from my nested translation key'
        >>> # this is roughly equivalent to `translate("hello").format(name="world")`
        >>> translate("hello", name="world")
        'hello world'

        Parameters
        ----------
        default: Any
            The default value to return if the translation key cannot be found
        plurality: Union[:class:`int`, :class:`float`, :class:`str`]
            **Deprecated keyword argument, kept around for backwards compatibility.**
            You should use :class:`ICULocale` for this purpose instead, as they handle this natively
        """
        for x in keys:
            if isinstance(x, dict):
                kwargs.update(x)

        keys = tuple(x for x in keys if isinstance(x, str))
        if self.base_key:
            keys = (self.base_key, *keys)

        if plurality is not None:
            if isinstance(plurality, str):
                plurality = kwargs[plurality]
            # noinspection PyDeprecation
            plurality = self.locale.plurality(plurality)
            if plurality is not None:
                keys += (plurality,)

        keys = ".".join(keys)
        locale = next((x for x in self.locales if keys in x), None)
        if not locale:
            warnings.warn(
                f"Translation ID {keys!r} was not found in locales {self.locales.names!r}",
                RuntimeWarning,
                stacklevel=2,
            )

            if default is not undefined:
                return default
            if self.strict:
                raise KeyError(keys)
            return keys

        return locale.format(keys, **kwargs)

    def lazy(self, *keys: str, **kwargs) -> LazyStr:
        """Lazily translate a string

        All arguments that can normally be passed to :meth:`__call__` can also
        be passed to this, and will be used when retrieving the actual translated string.

        The translated string can be retrieved by either casting the returned
        :class:`~swift_libs.translations.utils.LazyStr` object to a str, by calling the LazyStr
        object similarly to a function, or attempting to access any normal str attribute.

        Example
        -------
        >>> translate = Translations(__file__)
        >>> translate('example')
        'hello, {name}'
        >>> translate.lazy('example')
        <LazyStr keys=('example',) kwargs={}>
        >>> translate.lazy('example')()
        'hello, {name}'
        >>> # keyword argument format arguments also work!
        >>> translate.lazy('example', name='world')()
        'hello, world'
        >>> # this also works:
        >>> str(translate.lazy('example'))
        'hello, {name}'
        >>> # you can also access normal str attributes:
        >>> translate.lazy('example').format(name='world')
        'hello, world'
        """
        return LazyStr(self, keys, kwargs)

    def sub(self, *keys: str, **kwargs):
        """Deprecated alias for :attr:`Translations.group`"""
        warnings.warn(
            "Translations.sub is deprecated, use Translations.group instead", DeprecationWarning
        )
        return self.group(*keys, **kwargs)

    def group(self, *keys: str, **kwargs) -> SubTranslations:
        # noinspection PyTypeChecker
        """Create a new group translator instance

        This works the same as if you simply specified ``base_key`` when creating a new
        Translations class instance.

        A group translator shares all the same locale and loader objects with the root translator.

        .. warning::
            The following keyword arguments are not supported by this method, and will
            raise a :class:`RuntimeError` if used:

            * ``loader``
            * ``locale``
            * ``base_key``
            * ``proxy``

        Example
        -------
        >>> from swift_libs.translations import MemoryLoader
        >>> loader = MemoryLoader({"en": {"sub": {"hello": "hello world"}}})
        >>> translate = Translations(__file__, loader=loader)
        >>> sub = translate.group("sub")
        >>> sub('hello')
        'hello world'
        """
        conflicts = [
            k for k in ("loader", "locale_type", "locale", "base_key", "proxy") if k in kwargs
        ]
        if conflicts:
            raise RuntimeError(f"One or more conflicting kwargs were specified: {conflicts!r}")
        kwargs.setdefault("strict", self.strict)
        return SubTranslations(
            parent=self,
            base_key=".".join([self.base_key, *keys] if self.base_key else keys),
            **kwargs,
        )


class SubTranslations(Translations):
    """Grouped translator returned by :func:`Translations.group`

    Group translators share the same :class:`LocaleProxy` with the root translator.
    """

    def __init__(self, parent: Translations, **kwargs):
        self.parent = parent
        super().__init__(None, proxy=parent.locales, **kwargs)

    @property
    def locales(self) -> LocaleProxy:
        return self.root.locales

    @locales.setter
    def locales(self, _):
        pass

    @property
    def root(self) -> Translations:
        p = self.parent
        while hasattr(p, "parent"):
            p = p.parent
        return p

    def generic(self, *keys: str, **kwargs):
        """Get a string from the root translator

        This can be useful if your locale root contains a collection of generic strings
        and use sub-translators to keep everything clean and organized.
        """
        # pylint wtf yes this is callable shut the fuck up
        return self.root(*keys, **kwargs)  # pylint:disable=not-callable
