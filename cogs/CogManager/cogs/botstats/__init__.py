from redbot.core.bot import Red

from cog_shared.swift_libs.checks import try_import
from cog_shared.swift_libs.setup import setup_cog


async def setup(bot: Red):
    try:
        setup_cog(bot, "BotStats", require_version="0.0.3a0")
    except TypeError:
        from redbot.core.errors import CogLoadError

        raise CogLoadError(
            "Your bot is running an outdated version of the shared library this"
            " cog depends on. You can resolve this issue by either running"
            "`[p]swiftlibs reload`, or by restarting your bot."
        )

    try_import("datadog")

    from .botstats import BotStats
    import datadog

    cog = BotStats(bot)
    datadog.initialize(statsd_host=await cog.config.host())
    cog.interval = await cog.config.interval()
    cog.prefix = await cog.config.prefix()
    cog.task = bot.loop.create_task(cog.stats_task())

    bot.add_cog(cog)
