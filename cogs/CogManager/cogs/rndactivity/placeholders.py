from datetime import datetime
from statistics import mean
from typing import Tuple, Iterable, List, Optional

from babel.dates import format_timedelta
from redbot.core.bot import Red

from parse import parse
from rndactivity.shared import translate, log
from cog_shared.swift_libs.setup import get_instance

warned_deprecated = set()


class Placeholder:
    def __init__(self, func, deprecated: bool = False, aliases: List[str] = None, name: str = None):
        self._func = func
        self.name = func.__name__ if name is None else name
        self.deprecated = deprecated
        self.aliases = aliases or []

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Placeholder name={self.name!r} aliases={self.aliases!r}>"

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)


def placeholder(
    maybe_func=None, *, name: str = None, deprecated: bool = False, aliases: List[str] = None
):
    def decorator(func):
        return Placeholder(func, deprecated=deprecated, aliases=aliases, name=name)

    if maybe_func:
        return decorator(maybe_func)

    return decorator


class Placeholders:
    def __iter__(self) -> Iterable[Tuple[str, Placeholder]]:
        for k in dir(self):
            v = getattr(self, k)
            if isinstance(v, Placeholder):
                yield k, v

    def __str__(self):
        return "\n".join(
            f"**{{{k}}}** \N{EM DASH} {translate('placeholders', k)}"
            for k, v in self
            if not v.deprecated
        )

    def __init__(self, bot: Optional[Red], shard: int):
        self._bot = bot
        self._shard_id = shard

    @classmethod
    def parse(cls, status: str, bot: Red, shard: int, error_deprecated: bool = False):
        self = cls(bot, shard)
        placeholders = dict(self)
        keys = {}
        for plc in placeholders.values():
            keys[plc.name] = plc.name
            for alias in plc.aliases:
                keys[alias] = plc.name
        # Doing this also filters out invalid placeholders, and lets us filter down to just
        # invoking the placeholder parsers for what we need. This might be slightly unsafe,
        # but seeing as how this cog is restricted to the bot owner, this isn't something I'm
        # really concerned about, because we expect that the bot owner has at least the
        # slightest clue as to what they're doing.
        args = {k for k in parse(status, status.format(**keys)).named.values()}
        kwargs = {}
        log.debug("Extracted args %r from parse", args)
        for arg in args:
            plc: Placeholder = placeholders[arg]
            if plc.deprecated:
                if error_deprecated:
                    raise KeyError(arg)
                if arg not in warned_deprecated:
                    log.warning(
                        "%r is a deprecated placeholder and will be removed in the near"
                        " future, rendering any strings that contain it unable to be"
                        " chosen to be the bot's activity status.",
                        arg,
                    )
                    warned_deprecated.add(arg)
            val = plc(self)
            kwargs[plc.name] = val
            for alias in plc.aliases:
                kwargs[alias] = val
        return status.format(**kwargs)

    @placeholder(aliases=["guilds"])
    def servers(self) -> int:
        return len([x for x in self._bot.guilds if x.shard_id == self._shard_id])

    @placeholder
    def shard(self) -> int:
        return self._shard_id + 1

    @placeholder
    def shards(self) -> int:
        return self._bot.shard_count

    @placeholder(aliases=["lavalink", "music"])
    def playing_music(self) -> int:
        import lavalink

        return len(lavalink.active_players())

    @placeholder
    def members(self):
        return sum(len(x.members) for x in self._bot.guilds)

    @placeholder
    def users(self):
        return len(self._bot.users)

    @placeholder
    def channels(self):
        return sum(len(x.channels) for x in self._bot.guilds)

    @placeholder(deprecated=True)
    def avg_members(self):
        return mean(x.member_count for x in self._bot.guilds)

    @placeholder(deprecated=True)
    def max_members(self):
        return max(x.member_count for x in self._bot.guilds)

    @placeholder
    def uptime(self):
        return format_timedelta(
            datetime.utcnow() - get_instance().uptime, locale=translate.babel, format="narrow"
        )
