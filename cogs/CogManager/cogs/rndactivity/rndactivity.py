import re
from asyncio import sleep
from random import choice
from typing import List, Union, Optional, Tuple

import discord
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import escape, pagify, warning

from cog_shared.swift_libs.formatting import tick
from cog_shared.swift_libs.menus import confirm, PaginatedMenu
from cog_shared.swift_libs.time import FutureTime
from rndactivity.placeholders import Placeholders
from rndactivity.shared import translate, log
from swift_i18n import Humanize

TWITCH_REGEX = re.compile(r"<?(?:https?://)?twitch\.tv/[^ ]+>?", re.IGNORECASE)
Delay = FutureTime().min_time.minutes(5).default_period.minutes()


class ActivityTypeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        argument = argument.lower()
        if argument not in ("playing", "watching", "listening", "streaming"):
            raise commands.BadArgument
        return getattr(discord.ActivityType, argument)


@translate.cog("help.cog_class")
class RNDActivity(commands.Cog):
    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2042511098, force_registration=True)
        self.config.register_global(statuses=[], delay=600)
        self._running_tasks = [self.bot.loop.create_task(self.status_task())]

    def cog_unload(self):
        for task in self._running_tasks:
            task.cancel()

    @staticmethod
    def extract_status(data: Union[str, dict]) -> Tuple[int, str]:
        if isinstance(data, str):
            return 0, data
        return data.get("type", 0), data["game"]

    def format_status(self, status: Union[str, dict], shard: int = 0, **kwargs) -> discord.Activity:
        game_type = 0
        url = None
        if isinstance(status, dict):
            game_type: int = status.get("type", 0)
            url: Optional[str] = status.get("url")
            status: str = status.get("game")

        formatted = Placeholders.parse(status, self.bot, shard, **kwargs)
        # noinspection PyArgumentList
        return discord.Activity(name=formatted, url=url, type=discord.ActivityType(game_type))

    async def update_status(self, statuses: List[str]):
        if not statuses:
            return
        status = choice(statuses)
        for shard in self.bot.shards.keys():
            try:
                game = self.format_status(status, shard=shard)
            except KeyError as e:
                log.exception(
                    f"Encountered invalid placeholder while attempting to parse status "
                    f"#{statuses.index(status) + 1}, skipping status update.",
                    exc_info=e,
                )
                return
            await self.bot.change_presence(
                activity=game, status=self.bot.guilds[0].me.status, shard_id=shard
            )

    async def status_task(self):
        await self.bot.wait_until_ready()
        while True:
            try:
                await self.update_status(list(await self.config.statuses()))
            except Exception as e:
                log.exception("Failed to update bot status", exc_info=e)
            await sleep(int(await self.config.delay()))

    ##############################################

    # noinspection PyTypeChecker
    @commands.group()
    @checks.is_owner()
    @checks.bot_in_a_guild()
    @translate.command("help.root", placeholders=Placeholders(None, 0))
    async def rndactivity(self, ctx: commands.Context):
        pass

    @rndactivity.command(name="delay")
    @translate.command("help.delay")
    async def rndactivity_delay(self, ctx: commands.Context, *, duration: Delay):
        await self.config.delay.set(duration.total_seconds())
        await ctx.send(tick(translate("delay_set", duration=Humanize(duration))))

    @rndactivity.command(name="add", usage="[activity_type=playing] <status>")
    @translate.command("help.add")
    async def rndactivity_add(
        self, ctx: commands.Context, game_type: Optional[ActivityTypeConverter], *, game: str
    ):
        stream = None
        if game_type is None:
            game_type = discord.ActivityType.playing
        elif game_type == discord.ActivityType.streaming:
            game = game.split(" ")
            stream, game = game.pop(), " ".join(game)
            if not TWITCH_REGEX.match(stream):
                raise commands.BadArgument(translate("no_stream_provided"))
        activity = {
            "type": game_type.value,
            "game": game,
            "url": stream.strip("<>") if stream else None,
        }

        try:
            self.format_status(activity, error_deprecated=True)
        except KeyError as e:
            await ctx.send(warning(translate("parse_fail_invalid_placeholder", placeholder=str(e))))
        else:
            async with self.config.statuses() as statuses:
                statuses.append(activity)
                await ctx.send(tick(translate("added_status", id=len(statuses))))

    @rndactivity.command(name="parse")
    @translate.command("help.parse")
    async def rndactivity_parse(self, ctx: commands.Context, *, status: str):
        shard = getattr(ctx.guild, "shard_id", 0)

        try:
            result = self.format_status(status, shard=shard, error_deprecated=True)
        except KeyError as e:
            await ctx.send(
                warning(
                    translate(
                        "parse_fail_invalid_placeholder",
                        placeholder=escape(str(e), mass_mentions=True),
                    )
                )
            )
        else:
            await ctx.send(
                translate(
                    "parse_result",
                    input=escape(status, mass_mentions=True),
                    result=escape(result.name, mass_mentions=True),
                )
            )

    @rndactivity.command(name="remove", aliases=["delete"])
    @translate.command("help.remove")
    async def rndactivity_remove(self, ctx: commands.Context, status: int):
        async with self.config.statuses() as statuses:
            if len(statuses) < status:
                return await ctx.send(warning(translate("non_existant_status", id=status)))

            removed = statuses.pop(status - 1)
            if not statuses:
                await self.bot.change_presence(
                    activity=None, status=getattr(ctx.me, "status", None)
                )
        removed = escape(self.extract_status(removed)[1], mass_mentions=True)
        await ctx.send(tick(translate("status_removed", id=status, status=removed)))

    @rndactivity.command(name="list")
    @translate.command("help.list")
    async def rndactivity_list(self, ctx: commands.Context):
        statuses = list(await self.config.statuses())
        if not statuses:
            return await ctx.send(warning(translate("no_setup_statuses", prefix=ctx.prefix)))

        pages = []
        for status in statuses:
            index = statuses.index(status) + 1
            game_type = 0
            stream_url = None
            if isinstance(status, dict):
                game_type = status.get("type", 0)
                stream_url = status.get("url")
                status = status.get("game")
            status = escape(status, formatting=True, mass_mentions=True)
            if stream_url:
                status = f"[{status}]({stream_url})"
            pages.append(
                f"**#{index}** \N{EM DASH} **{translate('game_type')[game_type]}** {status}"
            )

        colour = await ctx.embed_colour()
        pages = [discord.Embed(colour=colour, description=x) for x in pagify("\n".join(pages))]
        await PaginatedMenu(
            pages=pages, bot=ctx.bot, channel=ctx.channel, member=ctx.author
        ).prompt()

    @rndactivity.command(name="clear")
    @translate.command("help.clear")
    async def rndactivity_clear(self, ctx: commands.Context):
        amount = len(await self.config.statuses())
        if await confirm(ctx, content=translate("clear_confirm", amount=amount)):
            await self.config.statuses.set([])
            await self.bot.change_presence(activity=None, status=self.bot.guilds[0].me.status)
            await ctx.send(tick(translate("clear_success", amount=amount)))
        else:
            await ctx.send(translate("ok_then"))
