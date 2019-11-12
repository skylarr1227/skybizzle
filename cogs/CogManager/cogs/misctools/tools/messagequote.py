from typing import Optional, Tuple

import discord
from redbot.core.utils.chat_formatting import escape

from cog_shared.swift_libs.formatting import message_link
from misctools import commands
from misctools.shared import translate as translate_
from misctools.toolset import Toolset

translate = translate_.group("messagequote")


class CrossGuildMessageConverter(commands.Converter):
    # noinspection PyRedundantParentheses
    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> Tuple[Optional[discord.TextChannel], int]:
        if argument.isnumeric():
            return (None, int(argument))

        arg = argument.split("-")
        if len(arg) != 2 or not all(x.isnumeric() for x in arg):
            raise commands.BadArgument(
                translate("invalid_id", mid=escape(argument, mass_mentions=True, formatting=True))
            )

        cid, mid = tuple(int(x) for x in arg)
        channel: discord.TextChannel = ctx.bot.get_channel(cid)

        # ensure the channel exists and is in a guild context
        guild: Optional[discord.Guild] = getattr(channel, "guild", None)
        if not channel or not guild or ctx.author not in guild.members:
            raise commands.BadArgument(translate("no_such_channel", id=cid))

        if not channel.permissions_for(guild.get_member(ctx.author.id)).read_message_history:
            # we're returning the generic no such channel string if the command invoker is not in
            # the guild the specified channel is in, so at this point it's safe to say if you're
            # determined enough, you could probably figure out that a channel exists with a given
            # ID given that the Discord API makes no real attempts to hide them, which makes
            # returning a generic not found message pointless.
            raise commands.BadArgument(translate("no_history_perms", id=cid))
        return (channel, mid)


async def maybe_retrieve(
    ctx: commands.Context, mid: int
) -> Optional[Tuple[discord.TextChannel, discord.Message]]:
    for channel in ctx.guild.channels:
        if not isinstance(channel, discord.TextChannel):
            continue

        # ensure we have permissions to retrieve message history to avoid sending
        # requests that will just end up with us getting a forbidden error
        # noinspection PyTypeChecker
        if not channel.permissions_for(ctx.me).read_message_history:
            continue
        # similarly, don't allow users to retrieve messages they can't normally retrieve
        if not channel.permissions_for(ctx.author).read_message_history:
            continue

        try:
            message = await channel.fetch_message(mid)
            # noinspection PyRedundantParentheses
            return (channel, message)
        except discord.HTTPException:
            pass
    raise RuntimeError


class MessageQuote(Toolset, i18n=translate):
    @commands.command(aliases=["mq"], usage="<ids...>")
    @commands.guild_only()
    @translate.command("help")
    async def messagequote(self, ctx: commands.Context, *message_ids: CrossGuildMessageConverter):
        # noinspection PyTypeChecker
        ids: Tuple[Optional[discord.TextChannel], int] = message_ids
        if not message_ids:
            await ctx.send_help()
            return

        for channel, mid in ids:
            message: Optional[discord.Message] = None

            if channel is not None:
                try:
                    message = await channel.fetch_message(mid)
                except discord.HTTPException:
                    pass
            else:
                try:
                    channel, message = await maybe_retrieve(ctx, mid)
                except (discord.HTTPException, RuntimeError):
                    pass

            if message is None:
                await ctx.send(translate("not_found", mid=mid))
            else:
                embed = discord.Embed(
                    colour=message.author.colour,
                    description=message.content,
                    timestamp=message.created_at,
                ).set_author(
                    name=message.author.display_name,
                    icon_url=message.author.avatar_url_as(format="png"),
                )

                if message.attachments:
                    embed.add_field(
                        name=translate("attachments"),
                        value="\n".join(
                            f"**\N{BULLET}** [`{x.filename}`]({x.url})" for x in message.attachments
                        ),
                    )

                embed.add_field(name="\N{ZERO WIDTH JOINER}", value=message_link(message))
                await ctx.send(
                    content=translate("sent_in", mid=mid, channel=message.channel.mention),
                    embed=embed,
                )
