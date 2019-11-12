from math import ceil
from typing import Dict, List, Union, Optional

import discord

from cog_shared.swift_libs.formatting import mention
from cog_shared.swift_libs.helpers import chunks
from cog_shared.swift_libs.menus import PaginatedMenu
from cog_shared.swift_libs.permissions import format_permission
from misctools import commands
from misctools.shared import translate as translate_
from misctools.toolset import Toolset
from swift_i18n import Humanize

translate = translate_.group("permbd")
perm_channel_types = {
    discord.TextChannel: (
        # read_messages isn't included here as voice channels use it as the view channel permission
        "add_reactions",
        "send_messages",
        "send_tts_messages",
        "manage_messages",
        "embed_links",
        "attach_files",
        "read_message_history",
        "mention_everyone",
        "external_emojis",
    ),
    discord.VoiceChannel: (
        "connect",
        "speak",
        "mute_members",
        "deafen_members",
        "move_members",
        "use_voice_activation",
        "priority_speaker",
        "stream",
    ),
}


def is_applicable(perm: str, channel: discord.abc.GuildChannel):
    try:
        ctype, _ = discord.utils.find(lambda x: perm in x[1], perm_channel_types.items())
        return isinstance(channel, ctype)
    except TypeError:
        return True


class PermBD(Toolset, i18n=translate):
    @commands.command(aliases=["permbd"])
    @commands.guild_only()
    @translate.command("help")
    async def permissionbreakdown(
        self,
        ctx: commands.Context,
        member: discord.Member = None,
        channel: Union[discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel] = None,
        list_all: bool = False,
    ):
        member = member or ctx.author
        channel = channel or ctx.channel

        role_perms: Dict[str, List[discord.Role]] = {
            x: [
                r
                for r in reversed(member.roles)
                if getattr(r.permissions, str(x), False) is True
                or r.permissions.administrator is True
            ]
            for x, y in discord.Permissions()
            if list_all or is_applicable(x, channel)
        }

        pages = list(chunks(list(role_perms.items()), ceil(len(role_perms) / 5)))
        total_pages = len(pages)
        for page in pages.copy():
            index = pages.index(page)
            page = self.__converter(
                page=page,
                member=member,
                channel=channel,
                page_id=index + 1,
                total_pages=total_pages,
                colour=await ctx.embed_colour(),
            )
            pages[index] = page

        await PaginatedMenu(
            bot=self.bot, member=ctx.author, channel=ctx.channel, pages=pages
        ).prompt(timeout=90)

    def __converter(
        self,
        channel: discord.TextChannel,
        member: discord.Member,
        page: dict,
        page_id: int,
        total_pages: int,
        colour: Union[discord.Colour, type(discord.Embed.Empty)] = discord.Embed.Empty,
    ):
        embed = discord.Embed(
            colour=colour,
            title=translate("name"),
            description=translate("subhead", member=member.mention, channel=channel.mention),
        )

        for perm, roles in page:
            list_roles = self.__trim_to_three(roles) if roles else []
            value = [
                translate("granted_by", n=len(roles), roles=", ".join(list_roles))
                if roles
                else translate("not_granted")
            ]

            overwrites = self.__build_overwrites(channel, member, perm)
            value.extend(
                [
                    translate(
                        "overwrites",
                        tid,
                        n=len(ow_roles),
                        overwrites=", ".join(self.__trim_to_three(ow_roles)),
                    )
                    for tid, ow_roles in overwrites.items()
                    if ow_roles
                ]
            )

            value.append(
                translate(
                    "final_value",
                    value="granted"
                    if getattr(channel.permissions_for(member), perm, False) is True
                    else "denied",
                )
            )

            embed.add_field(name=format_permission(perm), value="\n".join(value), inline=False)

        return embed.set_footer(text=translate.generic("page", current=page_id, total=total_pages))

    @staticmethod
    def __build_overwrites(channel: discord.abc.GuildChannel, member: discord.Member, perm: str):
        overwrites: Dict[Union[discord.Member, discord.Role], Optional[bool]] = {
            x: getattr(y, perm, None)
            for x, y in getattr(channel.overwrites, "items", lambda: channel.overwrites)()
            if x == member or x in member.roles and getattr(y, perm, None) is not None
        }
        return {
            "granted": [k for k, v in overwrites.items() if v is True],
            "denied": [k for k, v in overwrites.items() if v is False],
        }

    @staticmethod
    def __trim_to_three(roles: List[discord.Role]) -> List[str]:
        new_list = [mention(x) for x in roles[:3]]
        if len(roles) > 3:
            new_list.append(translate("n_more", n=Humanize(len(roles) - 3)))
        return new_list
