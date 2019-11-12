from datetime import datetime
from typing import Tuple

import discord
from babel.dates import format_timedelta
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import bold

from misctools import commands
from misctools.shared import translate as translate_, log
from misctools.toolset import Toolset
from cog_shared.swift_libs.setup import get_instance

try:
    import psutil
except ImportError:
    psutil = None

translate = translate_.group("stats")


class Stats(Toolset, i18n=translate):
    bot: Red

    def toolset_before_setup(self):
        if psutil is None:
            log.warning(
                "psutil is not available; the statistics toolset will not display"
                " host system resource utilization. This can be resolved by"
                " using `[p]pipinstall psutil` in any channel I can access."
            )

    @staticmethod
    def __sys_info() -> dict:
        if psutil is None:
            return {}

        process = psutil.Process()

        return {
            "cpu": psutil.cpu_percent(),
            "mem": (process.memory_percent(), process.memory_full_info().uss),
            "threads": process.num_threads(),
        }

    def __channels(self) -> Tuple[int, int]:
        all_channels = {}
        for channel in self.bot.get_all_channels():
            channel_type = type(channel)
            if channel_type not in all_channels:
                all_channels[channel_type] = 0
            all_channels[channel_type] += 1

        return all_channels.get(discord.TextChannel, 0), all_channels.get(discord.VoiceChannel, 0)

    @commands.command(aliases=["statistics"])
    @translate.command("help")
    async def stats(self, ctx: commands.Context):
        embed = discord.Embed(colour=await ctx.embed_colour())
        embed.set_author(
            name=translate("bot_stats"), icon_url=self.bot.user.avatar_url_as(format="png")
        )

        embed.add_field(
            name=translate("uptime"),
            value=format_timedelta(
                datetime.utcnow() - get_instance().uptime, locale=translate.locale.babel
            ),
        )

        embed.add_field(name=translate("users"), value=str(len(self.bot.users)))
        embed.add_field(name=translate("guilds"), value=str(len(self.bot.guilds)))

        text, voice = self.__channels()
        embed.add_field(
            name=translate("channels"), value=translate("channel_stats", text=text, voice=voice)
        )

        sl = get_instance()
        embed.add_field(name=translate("messages"), value=str(sl.messages_read))
        embed.add_field(name=translate("commands_ran"), value=str(sl.processed_commands))

        embed.add_field(name=translate("cogs"), value=str(len(self.bot.cogs)))
        embed.add_field(name=translate("commands"), value=str(len(self.bot.commands)))

        embed.add_field(name="\N{ZERO WIDTH JOINER}", value="\N{ZERO WIDTH JOINER}")

        sys_stats = self.__sys_info()
        if any(sys_stats.keys()):
            embed.add_field(
                name="\N{ZERO WIDTH JOINER}", value="\N{ZERO WIDTH JOINER}", inline=False
            )
            embed.add_field(name=translate("cpu_usage"), value=f"{sys_stats['cpu']:.1f}%")
            embed.add_field(
                name=translate("memory"),
                value=f"{sys_stats['mem'][1] / 1024 / 1024:.1f} MB ({sys_stats['mem'][0]:.2f}%)",
            )
            embed.add_field(name=translate("threads"), value=str(sys_stats["threads"]))

        embed._fields = [  # pylint:disable=protected-access
            {k: bold(v) if k == "name" and len(v) > 1 else v for k, v in x.items()}
            for x in embed._fields  # pylint:disable=protected-access
        ]

        await ctx.send(embed=embed)
