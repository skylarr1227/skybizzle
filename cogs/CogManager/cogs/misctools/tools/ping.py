from babel.units import format_unit
from redbot.core.bot import Red

from misctools import commands
from misctools.shared import translate as translate_
from misctools.toolset import Toolset
from swift_i18n import Humanize

translate = translate_.group("ping")


class PingTime(Toolset, i18n=translate):
    bot: Red
    conflict_ok = ["ping"]

    # noinspection PyAttributeOutsideInit
    def toolset_before_setup(self):
        # unmentioned breaking changes in a patch release <angry grumbling>
        self.orig_ping = self.bot.get_command("ping")  # pylint:disable=W0201
        if self.orig_ping:
            self.bot.remove_command(self.orig_ping.qualified_name)

    def toolset_cleanup(self):
        if self.orig_ping:
            self.bot.add_command(self.orig_ping)
        else:
            self.bot.add_command(self.bot.get_cog("Core").ping)

    @commands.command(aliases=["pingtime"])
    @translate.command("help")
    async def ping(self, ctx: commands.Context):
        await ctx.send(
            translate(
                "ping",
                latency=Humanize(
                    format_unit,
                    dict(self.bot.latencies)[ctx.guild.shard_id if ctx.guild else 0] * 1000,
                    "millisecond",
                ),
            )
        )
