from typing import Optional

import discord
from redbot.core import checks, commands, modlog
from redbot.core.bot import Config, Red
from redbot.core.utils.chat_formatting import warning

from cog_shared.swift_libs.checks import cogs_loaded, hierarchy_allows
from cog_shared.swift_libs.formatting import tick
from cog_shared.swift_libs.time import FutureTime
from swift_i18n import Humanize
from timedmute.shared import translate

TimeConverter = FutureTime().min_time.minutes(2).default_period.hours()


@translate.cog("help.cog")
class TimedMute(commands.Cog):
    OVERWRITE_PERMISSIONS = discord.PermissionOverwrite(
        speak=False, send_messages=False, add_reactions=False
    )

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=12903812, force_registration=True)
        self.config.register_guild(punished_role=None)
        self._cases_task = self.bot.loop.create_task(self._setup_cases())

    def cog_unload(self):
        self._cases_task.cancel()

    @staticmethod
    async def _setup_cases():
        try:
            await modlog.register_casetype(
                name="timedmute",
                default_setting=True,
                # as much as I've love to be able to translate this string, it can't really be
                # reasonably done, as case names aren't translated in core Red cogs,
                # and there's no real reasonable way to translate them.
                case_str="Timed Mute",
                image="\N{STOPWATCH}\N{SPEAKER WITH CANCELLATION STROKE}",
            )
        except RuntimeError:
            pass

    async def setup_overwrites(self, role: discord.Role, channel: discord.abc.GuildChannel):
        # noinspection PyUnresolvedReferences
        if not channel.permissions_for(channel.guild.me).manage_roles:
            return
        await channel.set_permissions(
            target=role,
            overwrite=self.OVERWRITE_PERMISSIONS,
            reason=translate("setup_audit_reason"),
        )

    async def setup_role(self, guild: discord.Guild) -> discord.Role:
        role = await guild.create_role(
            name=translate("role_name"), permissions=discord.Permissions.none()
        )

        for channel in guild.channels:
            await self.setup_overwrites(role, channel)

        await self.config.guild(guild).punished_role.set(role.id)
        return role

    async def get_punished_role(self, guild: discord.Guild) -> Optional[discord.Role]:
        return discord.utils.get(guild.roles, id=await self.config.guild(guild).punished_role())

    @commands.command(aliases=["tempmute"])
    @commands.guild_only()
    @cogs_loaded("TimedRole")
    @checks.mod_or_permissions(manage_roles=True)
    @checks.bot_has_permissions(manage_roles=True)
    @translate.command("help.command")
    async def timedmute(
        self,
        ctx: commands.Context,
        member: discord.Member,
        duration: TimeConverter,
        *,
        reason: str = None,
    ):
        from timedrole.api import TempRole

        if not await hierarchy_allows(self.bot, mod=ctx.author, member=member):
            await ctx.send(warning(translate("hierarchy_disallows")))
            return

        role = await self.get_punished_role(ctx.guild)
        if role is None:
            tmp_msg = await ctx.send(translate("setting_up"))
            async with ctx.typing():
                role = await self.setup_role(ctx.guild)
            await tmp_msg.delete()

        if role in member.roles:
            await ctx.send(warning(translate("already_muted")))
            return

        role = await TempRole.create(
            member, role, duration=duration, added_by=ctx.author, reason=reason
        )
        await role.apply_role(reason=reason)

        try:
            await modlog.create_case(
                bot=self.bot,
                guild=ctx.guild,
                user=member,
                moderator=ctx.author,
                reason=reason,
                until=role.expires_at,
                action_type="timedmute",
                created_at=role.added_at,
            )
        except RuntimeError:
            pass

        await ctx.send(tick(translate("member_muted", member=member, duration=Humanize(duration))))

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        # noinspection PyUnresolvedReferences
        guild: discord.Guild = channel.guild
        if not channel.permissions_for(guild.me).manage_roles:
            return
        role = await self.get_punished_role(guild)
        if not role:
            return
        await self.setup_overwrites(role, channel)
