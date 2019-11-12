from __future__ import annotations

import logging
import warnings
from typing import TypeVar, Callable, Union, Type

from redbot.core.commands import Command, Cog
from redbot.core.i18n import get_locale

from swift_i18n import Translator as _Translator, TranslatorGroup as _TranslatorGroup
from swift_i18n.util import LazyStr, log

# noinspection PyShadowingBuiltins
_T = TypeVar("_T")

if len(log.handlers) == 1:
    rlog = logging.getLogger("red")
    for handler in rlog.handlers:
        log.addHandler(handler)
    log.setLevel(rlog.level)
    del rlog


class Translator(_Translator):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("locales", get_locale)
        super().__init__(*args, **kwargs)

    def __contains__(self, item):
        if self.base_key:
            item = ".".join([self.base_key, item])
        return any(item in x for x in self.locales)

    @property
    def babel(self):
        warnings.warn(
            "Translator.babel is deprecated; use the Humanize wrapper class for"
            " format arguments instead",
            DeprecationWarning,
        )
        return self.locale.babel

    def _partial(self, *keys, **kwargs):
        return lambda *_, **__: self(*keys, **kwargs)

    def command(self, *keys: str, **kwargs) -> Callable[[_T], _T]:
        # noinspection PyUnresolvedReferences
        """Decorator to replace command help doc strings with translated strings

        All regular call arguments able to be passed to :class:`Translator` objects may be used
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
    def attach_to_commands(self, cls: _T) -> _T:
        """Attach this translator to commands in the given class

        Using this method directly should really only prove to be useful if you're using an
        unconventional setup for a cog, or if you don't want your cog's help documentation
        to be ran through Translations.

        This method may also be used as a decorator in place of :attr:`cog`::

            >>> translate = Translator(__file__)
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

        .. note::
            This method replaces the ``help`` :class:`property` in your cog class.
            Unless you're doing some really weird things, this should be harmless.

        Example
        -------
        >>> translate = Translator(__file__)
        >>> @translate.cog("help.cog_class")
        ... class MyCog(commands.Cog):
        ...     pass  # do stuff
        ...
        >>> def setup(bot):
        ...     # ...
        ...     bot.add_cog(MyCog())
        ...     # ...
        ...

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

    def sub(self, *a, **kw):
        warnings.warn(
            "Translator.sub is deprecated; use Translator.group instead", DeprecationWarning
        )
        return self.group(*a, **kw)

    def group(self, *keys: str, **kwargs) -> TranslatorGroup:
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


class TranslatorGroup(Translator, _TranslatorGroup):
    pass
