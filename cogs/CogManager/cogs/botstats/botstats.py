import asyncio
import logging
from typing import Optional

from datadog import statsd
from redbot.core import Config, commands, checks
from redbot.core.bot import Red

from cog_shared.swift_libs.i18n import Translator
from cog_shared.swift_libs.setup import get_instance

translate = Translator(__file__)
log = logging.getLogger("red.botstats")


@translate.cog("help._root")
class BotStats(commands.Cog):
    # noinspection PyTypeChecker
    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.task: Optional[asyncio.Task] = None
        self.config = Config.get_conf(self, identifier=1278435453, force_registration=True)
        self.config.register_global(host="127.0.0.1", interval=5, prefix="bot", cmd_counter=True)
        self.interval: int = None
        self.prefix: str = None
        self.cmd_counter: bool = True

    def cog_unload(self):
        self.__unload()

    def __unload(self):
        if self.task is not None:
            self.task.cancel()

    @commands.group()
    @checks.is_owner()
    @translate.command("help.botstats._root")
    async def botstats(self, ctx: commands.Context):
        pass

    @botstats.command(name="host")
    @translate.command("help.botstats.host")
    async def botstats_host(self, ctx: commands.Context, host: str):
        await self.config.host.set(host)
        await ctx.send(translate("host_set"))

    @botstats.command(name="interval")
    @translate.command("help.botstats.interval")
    async def botstats_interval(self, ctx: commands.Context, seconds: int):
        await self.config.interval.set(seconds)
        self.interval = seconds
        await ctx.send(translate("interval_set"))

    @botstats.command(name="prefix")
    @translate.command("help.botstats.prefix")
    async def botstats_prefix(self, ctx: commands.Context, prefix: str = "bot"):
        await self.config.prefix.set(prefix)
        self.prefix = prefix
        await ctx.send(translate("prefix_set"))

    @botstats.command(name="counters")
    @translate.command("help.botstats.counter")
    async def botstats_counter(self, ctx: commands.Context):
        new_val = not await self.config.cmd_counter()
        await self.config.cmd_counter.set(new_val)
        self.cmd_counter = new_val
        await ctx.send(translate("cmds_using_{}".format("counters" if new_val else "gauges")))

    ######################

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            if self.task and not self.task.done():
                return
        except asyncio.InvalidStateError:
            pass
        except asyncio.CancelledError:
            log.warning("Stats task was cancelled, but somehow got a ready event")
            return
        self.task = self.bot.loop.create_task(self.stats_task())

    async def stats_task(self):
        await self.bot.wait_until_ready()
        sl = get_instance()
        while True:
            if not self.cmd_counter:
                statsd.gauge(f"{self.prefix}.commands", sl.processed_commands)
                statsd.gauge(f"{self.prefix}.messages", sl.messages_read)
            # ping is being displayed as a gauge, since reporting it as a timing makes it look
            # absolutely disgusting w/ netdata: https://u.odinair.xyz/khKWoFYk.png
            statsd.gauge(f"{self.prefix}.ping", self.bot.latency)
            statsd.gauge(f"{self.prefix}.guilds", len(self.bot.guilds))
            statsd.gauge(f"{self.prefix}.users", len(self.bot.users))
            statsd.gauge(
                f"{self.prefix}.text_channels", sum(len(g.text_channels) for g in self.bot.guilds)
            )
            statsd.gauge(
                f"{self.prefix}.voice_channels", sum(len(g.voice_channels) for g in self.bot.guilds)
            )
            statsd.gauge(f"{self.prefix}.voice_audience", self.voice_audience)
            await asyncio.sleep(self.interval)

    @commands.Cog.listener()
    async def on_message(self, *_):
        if self.cmd_counter:
            statsd.increment(f"{self.prefix}.messages", 1)

    @commands.Cog.listener()
    async def on_command(self, *_):
        if self.cmd_counter:
            statsd.increment(f"{self.prefix}.commands", 1)

    ######################

    @property
    def voice_audience(self) -> int:
        return sum(
            sum(not m.bot for m in c.members)
            for g in self.bot.guilds
            for c in g.voice_channels
            if g.get_member(self.bot.user.id) in c.members
        )
