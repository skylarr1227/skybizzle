import copy
import unicodedata
from datetime import datetime
from inspect import getsource
from textwrap import dedent
from typing import Union

import discord
from babel.dates import format_timedelta, format_datetime
from redbot.core import checks
from redbot.core.utils import deduplicate_iterables
from redbot.core.utils.chat_formatting import warning, pagify, error, escape
from tzlocal import get_localzone

from cog_shared.swift_libs.checks import is_dev
from cog_shared.swift_libs.helpers import flatten
from misctools import commands
from misctools.shared import translate as translate_, log
from misctools.toolset import Toolset
from swift_i18n import Humanize

translate = translate_.group("dev")


class Dev(Toolset, i18n=translate):
    # This command is taken from jishaku:
    # https://github.com/Gorialis/jishaku/blob/fc7c479/jishaku/cog.py#L346-L359
    # noinspection PyProtectedMember
    @commands.command()
    @checks.is_owner()
    @is_dev()
    @translate.command("help.sudo")
    async def sudo(self, ctx: commands.Context, *, command: str):
        alt_message: discord.Message = copy.copy(ctx.message)
        # pylint:disable=protected-access
        if discord.version_info >= (1, 2, 0):
            alt_message._update({"content": ctx.prefix + command})
        else:
            # noinspection PyArgumentList
            alt_message._update(alt_message.channel, {"content": ctx.prefix + command})
        alt_ctx = await ctx.bot.get_context(alt_message, cls=type(ctx))
        # pylint:enable=protected-access

        if alt_ctx.command is None:
            return await ctx.send(
                translate.generic(
                    "command_missing",
                    command=escape(alt_ctx.invoked_with, mass_mentions=True, formatting=True),
                )
            )

        # bypass yes/no checks for commands that support it
        alt_ctx.assume_yes = True

        log.info("%s (%s) used sudo to invoke command: %r", ctx.author, ctx.author.id, command)
        return await alt_ctx.command.reinvoke(alt_ctx)

    @commands.command()
    @translate.command("help.rtfs")
    async def rtfs(self, ctx: commands.Context, *, command_name: str):
        command = self.bot.get_command(command_name)
        if command is None:
            await ctx.send(
                warning(
                    translate.generic(
                        "command_missing",
                        command=escape(command_name, mass_mentions=True, formatting=True),
                    )
                )
            )
            return

        try:
            callback = command.callback
            # a while loop handles the possibility of wrappers being on top of our existing wrappers
            # such as the @bank.cost decorator proposed in red#2761
            while hasattr(callback, "__wrapped__"):
                callback = callback.__wrapped__
            source = pagify(dedent(getsource(callback)))
        except OSError:
            await ctx.send(error(translate("cannot_retrieve")))
        else:
            await ctx.send_interactive(source, box_lang="py")

    @commands.command(usage="<characters...>")
    @translate.command("help.charinfo")
    async def charinfo(self, ctx: commands.Context, *characters: Union[discord.PartialEmoji, str]):
        if not characters:
            await ctx.send_help()
            return

        characters = flatten(
            [x if isinstance(x, discord.PartialEmoji) else list(x) for x in characters]
        )
        characters = deduplicate_iterables(
            [
                x
                for x in characters
                # filter out space characters, as these usually aren't what we're being requested
                # to retrieve info on, and it's almost entirely useless to use an escape
                # sequence to get a mere space character
                if x != " "
            ]
        )

        if len(characters) > 25:
            await ctx.send_help()
            return

        # the following is - for all intents and purposes - ripped directly from RDanny:
        # https://github.com/Rapptz/RoboDanny/blob/ee101d1/cogs/meta.py#L209-L223

        def to_str(char: Union[commands.PartialEmojiConverter, str]):
            if isinstance(char, discord.PartialEmoji):
                return f"{char} \N{EM DASH} `{char.id}`"
            else:
                digit = ord(char)
                name = unicodedata.name(char, translate("name_not_found"))
                return f"{char} \N{EM DASH} `{name}` (`\\U{digit:>08}`)"

        await ctx.send("\n".join(map(to_str, characters)))

    @commands.group(aliases=["snowflake", "createdat"], invoke_without_command=True)
    @translate.command("help.snowflake")
    async def snowflaketime(self, ctx: commands.Context, *snowflakes: int):
        if not snowflakes:
            await ctx.send_help()
            return

        await ctx.send_interactive(
            pagify(
                "\n".join(
                    [
                        "{}: {} \N{EM DASH} `{}`".format(
                            snowflake,
                            format_timedelta(
                                discord.utils.snowflake_time(snowflake) - datetime.utcnow(),
                                add_direction=True,
                                locale=translate.locale.babel,
                            ),
                            format_datetime(
                                discord.utils.snowflake_time(snowflake),
                                locale=translate.locale.babel,
                                tzinfo=get_localzone(),
                            ),
                        )
                        for snowflake in snowflakes
                    ]
                )
            )
        )

    @snowflaketime.command(name="delta")
    @translate.command("help.snowflake_delta")
    async def snowflake_delta(self, ctx: commands.Context, starting: int, ending: int):
        starting, ending = (
            discord.utils.snowflake_time(starting),
            discord.utils.snowflake_time(ending),
        )
        now = datetime.utcnow()

        await ctx.send(
            translate(
                "snowflake_delta",
                start_delta=Humanize(starting - now, add_direction=True),
                start_date=Humanize(starting),
                end_delta=Humanize(ending - now, add_direction=True),
                end_date=Humanize(ending),
                difference=Humanize(ending - starting),
            )
        )
