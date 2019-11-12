from __future__ import annotations

import asyncio
import importlib
import sys
from asyncio import Future
from collections import Counter
from contextlib import suppress
from datetime import datetime
from typing import Type, Union, Set, List, Optional

from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.utils import deduplicate_iterables
from redbot.core.utils.chat_formatting import inline, box

from . import __version__ as _sl_version
from ._internal import log, translate as translate_
from .checks import is_dev, sl_version
from .menus import confirm, PaginatedMenu
from .time import FutureTime

translate = translate_.group("util_cog")
__all__ = ("setup_cog", "get_instance")
loaded = {}
# Set of cog names that depend on swift_libs, used when '[p]swiftlibs reload' is invoked.
# Cogs in this set are not guaranteed to still be loaded.
dependents: Set[str] = set()
# Cogs that've requested a newer version of swift_libs than what is currently in memory,
# and as such require swift_libs to be reloaded before they can be loaded again.
# These are guaranteed to be unloaded.
require_update: Set[str] = set()


def maybe_get(package, var, default=None):
    from importlib import import_module

    try:
        mod = import_module(package)
    except ImportError:
        return default
    else:
        return getattr(mod, var, default)


# noinspection PyPep8Naming,PyProtectedMember
@translate.cog("help.cog")
class swift_libs(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        # yeah, thanks a lot. JusT maKe yOUr oWn cOUnTeR
        # <angry grumbling>
        self.counter = Counter()
        if hasattr(bot, "counter"):
            self.counter.update(**bot.counter)
        super().__init__()

    @commands.Cog.listener()
    async def on_message(self, _):
        self.counter["messages_read"] += 1

    @commands.Cog.listener()
    async def on_command(self, _):
        self.counter["processed_commands"] += 1

    @property
    def messages_read(self):
        return self.counter.get("messages_read", 0)

    @property
    def processed_commands(self):
        return self.counter.get("processed_commands", 0)

    @property
    def uptime(self) -> datetime:
        # > remove public attribute in one pr (red#2967)
        # > re-add it as a read only property in another (red#2976)
        # why have i not just made my own bot yet?
        if hasattr(self.bot, "uptime"):
            return self.bot.uptime
        elif hasattr(self.bot, "_uptime"):
            return self.bot._uptime
        else:
            raise AttributeError("unable to find bot uptime attribute")

    def sl_reload_hook(self, old: swift_libs):
        with suppress(AttributeError):
            self.counter["messages_read"] = old.messages_read
            self.counter["processed_commands"] = old.processed_commands

    @staticmethod
    def dump(prefix: str):
        dumped = 0
        for k in list(sys.modules.keys()):
            if k.startswith(prefix):
                dumped += 1
                del sys.modules[k]
        return dumped

    @commands.group(name="swiftlibs")
    @checks.is_owner()
    @translate.command("help.swiftlibs._root")
    async def swiftlibs(self, ctx):
        pass

    @swiftlibs.command(name="debuginfo", hidden=True)
    @translate.command("help.swiftlibs.info")
    @commands.check(lambda ctx: ctx.bot.get_command("debuginfo") is not None)
    async def sl_info(self, ctx: commands.Context):
        # We don't want embeds for something that will likely be attached to an issue,
        # and doing this also makes what we do to add our info significantly easier.
        f = Future()
        f.set_result(False)
        ctx.embed_requested = lambda *_, **__: f

        send = ctx.send
        debug_info: List[str] = []

        async def send_override(content):
            debug_info.append(content)

        # Closed course, professional driver. Don't attempt this on your own.
        try:
            ctx.send = send_override
            await ctx.invoke(self.bot.get_cog("Core").debuginfo)
        except Exception:
            ctx.send = send
            raise
        else:
            ctx.send = send

        debug_info = [x.replace("```", "").rstrip() for x in debug_info]
        versions = {
            "swift_libs": _sl_version,
            "swift_i18n": maybe_get("swift_i18n.meta", "__version__", "<unknown>"),
            "motor": maybe_get("motor", "version", "<not installed>"),
        }

        try:
            from redbot.core.drivers import PostgresDriver as _
        except ImportError:
            pass
        else:
            versions["asyncpg"] = maybe_get("asyncpg", "__version__", "<not installed>")

        debug_info.extend(["", *[f"{k} version: {v}" for k, v in versions.items()]])
        await ctx.send(box("\n".join(debug_info)))

    @swiftlibs.command(name="dump")
    @is_dev()
    @translate.command("help.swiftlibs.dump")
    async def sl_dump(self, ctx: commands.Context, module_prefix: str):
        await ctx.send(translate("dumped", count=self.dump(module_prefix)))

    @swiftlibs.command(name="reload")
    @translate.command("help.swiftlibs.reload")
    async def sl_reload(self, ctx: commands.Context, skip_confirmation: bool = False):
        self.dump(".".join(self.__module__.split(".")[:-1]))
        self.dump("swift_i18n")
        to_reload = [x.lower() for x in dependents if x in ctx.bot.cogs]
        to_reload.extend(map(lambda x: x.lower(), require_update))
        to_reload = deduplicate_iterables(to_reload)
        names = " ".join(inline(x) for x in to_reload)

        if skip_confirmation or await confirm(ctx, content=translate("reload_confirm", cogs=names)):
            await ctx.invoke(ctx.bot.get_cog("Core").reload, *to_reload)
        else:
            await ctx.send(translate("reload_manual", cogs=names))

    # These commands are intentionally untranslated.

    @swiftlibs.group(name="debug")
    @is_dev()
    async def sl_debug(self, ctx):
        pass

    @sl_debug.command(name="confirm")
    async def sldbg_confirm(self, ctx: commands.Context):
        """Bare-bones confirmation prompt"""
        await ctx.send(str(await confirm(ctx, content="y/n?")))

    @sl_debug.command(name="pmenu")
    async def sldbg_pmenu(self, ctx: commands.Context, pages: int = 5, timeout: int = 30):
        """Bare-bones paginated menu"""
        await PaginatedMenu(
            pages=[f"page {n}" for n in range(pages)],
            bot=ctx.bot,
            channel=ctx.channel,
            member=ctx.author,
        ).prompt(timeout=timeout)

    @sl_debug.command(name="transl")
    async def sldbg_transl(self, ctx: commands.Context, cog: str, key: str, *args):
        """Retrieve a translated string from a cog"""
        from .i18n import Translator

        args = [arg.split("=") for arg in args]
        args = {arg[0]: "=".join(arg[1:]) for arg in args if len(arg) >= 2}
        file = importlib.import_module(ctx.bot.get_cog(cog).__module__).__file__
        t = Translator(file)
        await ctx.send(t(key, **args))

    @sl_debug.command(name="time")
    async def sldbg_time(self, ctx: commands.Context, *, duration: FutureTime):
        """Return what `duration` resolves to"""
        from redbot.core.utils.chat_formatting import humanize_timedelta

        # noinspection PyTypeChecker
        await ctx.send(humanize_timedelta(timedelta=duration))


def get_instance() -> Optional[swift_libs]:
    """Get the current swift_libs cog instance"""
    # TODO: Replace this function with something less disgusting
    # This was never originally meant to be public, but unfortunately has to be because of
    # how we're working around Red's half-assed privatization of bot attributes
    return loaded.get("swift_libs")


def load_or_reload(bot: Red, load: Type[commands.Cog], *args, **kwargs):
    name = load.__name__
    if name not in loaded or loaded[name] is not bot.get_cog(name):
        old = bot.cogs.get(name)
        if old:
            log.debug("Unloading previously loaded version of internal cog %r", name)
            bot.remove_cog(name)
        log.info("Loading internal cog %r", name)
        loaded[name] = load = load(bot, *args, **kwargs)
        if old and hasattr(load, "sl_reload_hook"):
            load.sl_reload_hook(old)
        bot.add_cog(load)


def setup_cog(
    bot: Red, cog: Union[str, Type[commands.Cog], commands.Cog], *, require_version: str = None, **_
):
    """Setup function to be called before adding any cog dependent on swift_libs

    This does *not* add your cog to the bot, but instead sets up the internal swift_libs
    utility cog.

    Keyword arguments passed to this function that aren't recognized are silently discarded.
    """
    cog_name = (
        cog
        if isinstance(cog, str)
        else cog.__name__
        if isinstance(cog, type)
        else type(cog).__name__
    )

    if require_version is not None:
        sl_version(require_version, cog_name)

    load_or_reload(bot, swift_libs)
    dependents.add(cog_name)

    # Backwards compatibility for cogs that expect this to be awaitable
    f = asyncio.Future()
    f.set_result(None)
    return f
