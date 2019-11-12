from datetime import datetime
from typing import Union, Optional

import discord
from babel.lists import format_list
from redbot.core import checks
from redbot.core.utils.chat_formatting import escape, bold
from redbot.core.utils.common_filters import filter_invites
from tzlocal import get_localzone

from cog_shared.swift_libs.formatting import mention
from misctools import commands
from misctools.shared import translate as translate_
from misctools.toolset import Toolset
from swift_i18n import Humanize

translate = translate_.group("uinfo")
DATETIME_FORMAT = "MMM dd, yyyy"


class UInfo(Toolset, i18n=translate):
    async def get_names_and_nicks(self, member: Union[discord.Member, discord.User]):
        try:
            mod = self.bot.cogs["Mod"]
        except KeyError:
            return [], []

        names = await mod.settings.user(member).past_names()
        nicks = (
            await mod.settings.member(member).past_nicks()
            if isinstance(member, discord.Member)
            else []
        )

        if names:
            names = [filter_invites(escape(name, mass_mentions=True)) for name in names if name]
        if nicks:
            nicks = [filter_invites(escape(nick, mass_mentions=True)) for nick in nicks if nick]
        return names, nicks

    async def build_description(self, member: Union[discord.Member, discord.User]) -> str:
        in_guild = isinstance(member, discord.Member)
        desc = []

        if in_guild:
            desc.append(
                translate(f"status.{str(member.status)}")
                if f"status.{str(member.status)}" in translate
                else translate("status.unknown")
            )

            for activity in member.activities:
                desc.append(
                    translate(
                        "activity",
                        activity.type.name
                        if not isinstance(activity, discord.Spotify)
                        else "spotify",
                        artists=Humanize(getattr(member.activity, "artists", [])),
                        title=getattr(member.activity, "title", "???"),
                        name=member.activity.name,
                        url=getattr(member.activity, "url", None),
                        default=None,
                    )
                )

            if member.is_on_mobile():
                desc.append(translate("on_mobile"))

            if member.voice:
                desc.append(translate("voice", channel=member.voice.channel.mention))

        if member.bot:
            desc.append(translate("role.bot"))
        else:
            if await self.bot.is_owner(member):
                desc.append(translate("role.bot_owner"))
            if in_guild:
                if member.guild.owner.id == member.id:
                    desc.append(translate("role.guild_owner"))
                elif await self.bot.is_admin(member):
                    desc.append(translate("role.guild_admin"))
                elif await self.bot.is_mod(member):
                    desc.append(translate("role.guild_mod"))
                else:
                    desc.append(translate("role.guild_member"))
            else:
                desc.append(translate("role.non_member"))

        if in_guild:
            # This will only be visible on Red versions 3.1.4+
            boost_since: Optional[datetime] = getattr(member, "premium_since", None)
            if boost_since:
                desc.append(
                    translate(
                        "nitro_boost",
                        delta=Humanize(boost_since - datetime.utcnow()),
                        date=Humanize(boost_since, tzinfo=get_localzone(), format=DATETIME_FORMAT),
                    )
                )

            if member.nick:
                desc.append(translate("nickname", nick=bold(escape(member.nick, formatting=True))))

        # noinspection PyTypeChecker
        return "\n".join(filter(bool, desc))

    async def _user_info(self, ctx: commands.Context, member: Union[discord.Member, discord.User]):
        in_guild = isinstance(member, discord.Member)
        embed = discord.Embed(
            title=filter_invites(str(member)),
            colour=member.colour if member.colour.value != 0 else discord.Embed.Empty,
            description=await self.build_description(member),
        ).set_thumbnail(
            # discord.py 1.0.0 changes this to an Asset instance, which causes PyCharm to start
            # flipping the fuck out since it doesn't match the expected str type, despite
            # working perfectly fine.
            url=str(member.avatar_url_as(static_format="png"))
        )

        now = datetime.utcnow()
        member_n = (
            (sorted(member.guild.members, key=lambda m: m.joined_at or now).index(member) + 1)
            if in_guild
            else None
        )
        embed.set_footer(
            text=translate(
                "member_footer" if member_n is not None else "user_footer", n=member_n, id=member.id
            )
        )

        if in_guild:
            if member.joined_at is None:
                joined_guild = translate("unknown_join_date")
            else:
                joined_guild = translate(
                    "joined_server",
                    delta=Humanize(member.joined_at - ctx.message.created_at, add_direction=True),
                    absolute=Humanize(member.joined_at, DATETIME_FORMAT, tzinfo=get_localzone()),
                )
        else:
            joined_guild = None

        joined_discord = translate(
            "joined_discord",
            delta=Humanize(member.created_at - ctx.message.created_at, add_direction=True),
            absolute=Humanize(member.created_at, DATETIME_FORMAT, tzinfo=get_localzone()),
        )

        embed.add_field(
            name=translate("account_age"),
            value="\n".join(x for x in [joined_discord, joined_guild] if x is not None),
        )

        if in_guild:
            roles = list(reversed([mention(x) for x in member.roles if not x.is_default()]))
            cap = 40
            if len(roles) > cap:
                roles = [*roles[:cap], translate("more_roles", num=len(roles) - cap)]
            if roles:
                embed.add_field(
                    name=translate("server_roles"),
                    value=format_list(roles, locale=translate.locale.babel),
                    inline=False,
                )

        names, nicks = await self.get_names_and_nicks(member)
        if names:
            embed.add_field(name=translate("past_names"), value=", ".join(names), inline=False)
        if nicks:
            embed.add_field(name=translate("past_nicks"), value=", ".join(nicks), inline=False)

        await ctx.send(embed=embed)

    @commands.command(aliases=["uinfo", "whois"])
    @commands.guild_only()
    @checks.bot_has_permissions(embed_links=True)
    @translate.command("help.member")
    async def user(self, ctx: commands.Context, *, member: discord.Member = None):
        await self._user_info(ctx, member or ctx.author)

    @commands.command(aliases=["guser", "guinfo", "gwhois"])
    @commands.cooldown(rate=2, per=60, type=commands.BucketType.user)
    @checks.bot_has_permissions(embed_links=True)
    @translate.command("help.global")
    async def globaluser(self, ctx: commands.Context, *, user_id: int):
        user = self.bot.get_user(user_id)
        if user is None:
            raise commands.BadArgument(translate("user_not_found"))

        if ctx.guild and user in ctx.guild.members:
            user = discord.utils.get(ctx.guild.members, id=user.id)
        else:
            # require that the command invoker and the specified user have at least
            # one guild in common, or that the command invoker is the bot owner or a co-owner
            if not any(
                user in x.members and ctx.author in x.members for x in self.bot.guilds
            ) and not await self.bot.is_owner(ctx.author):
                raise commands.BadArgument(translate("user_not_found"))

        await self._user_info(ctx, user)
