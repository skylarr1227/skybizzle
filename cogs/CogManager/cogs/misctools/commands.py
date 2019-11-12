# pylint:disable=unused-wildcard-import,wildcard-import,protected-access,function-redefined

from functools import wraps
from typing import Optional, Callable

from redbot.core.commands import *
from redbot.core.commands import command as _command

"""
Yes, this is seriously another layer of classes on top of discord.py's command extensions.

The alternative would be a mess of fucking around with command attributes.

At least this way it's slightly clearer as to what that fucking around is doing.
"""


class _CommandMixin:
    _callback: Callable
    __original_kwargs__: dict

    def __init__(self, *args, **kwargs):
        # This class will be used when retrieving the command cog class, namely to force
        # this command to appear in [p]help MiscTools
        self._appear_from: Optional[Cog] = None
        # This is the actual self argument we want to use instead of _appear_from
        self._actual_self: Optional[Cog] = None
        # The actual cog according to discord.py
        self._cog: Optional[Cog] = None
        super().__init__(*args, **kwargs)
        self._callback_wrapper: Callable = self.__wrapper_cb()

    def __wrapper_cb(self):
        wrapped = self._callback

        @wraps(wrapped)
        async def cb(*args, **kwargs):
            if self._actual_self:
                args = list(args)[1:]
                args.insert(0, self._actual_self)
            return await wrapped(*args, **kwargs)

        return cb

    @property
    def callback(self):
        return getattr(self, "_callback_wrapper", self._callback)

    @callback.setter
    def callback(self, cb):
        # noinspection PyArgumentList
        Command.callback.fset(self, cb)  # pylint:disable=no-member
        # Wait until we've fully gone through __init__ before using our wrapper function
        if hasattr(self, "_callback_wrapper"):
            self._callback_wrapper = self.__wrapper_cb()

    def _ensure_assignment_on_copy(self, other):
        # noinspection PyProtectedMember,PyUnresolvedReferences
        other = super()._ensure_assignment_on_copy(other)
        other._appear_from = self._appear_from
        other._actual_self = self._actual_self
        other._cog = self._cog
        return other

    @property
    def cog(self):
        if self._appear_from:
            return self._appear_from
        return self._cog

    # noinspection PyShadowingNames
    @cog.setter
    def cog(self, cog):
        self._cog = cog

    def copy(self):
        ret = self.__class__(self._callback, **self.__original_kwargs__)
        return self._ensure_assignment_on_copy(ret)


# These are private properties to allow for isinstance(..., commands.Command)
class _Command(_CommandMixin, Command):
    pass


class _Group(_CommandMixin, Group):
    def command(self, *args, **kwargs) -> Callable[[Callable], "Command"]:
        def decorator(func):
            kwargs.setdefault("parent", self)
            result = command(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator

    def group(self, *args, **kwargs) -> Callable[[Callable], "Group"]:
        def decorator(func):
            kwargs.setdefault("parent", self)
            result = group(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator


def command(name=None, cls=_Command, **attrs) -> Callable[[Callable], Command]:
    return _command(name, cls, **attrs)


def group(name=None, **attrs) -> Callable[[Callable], Group]:
    return _command(name, _Group, **attrs)
