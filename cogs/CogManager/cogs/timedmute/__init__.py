from redbot.core.bot import Red
from redbot.core.errors import CogLoadError

from cog_shared.swift_libs.checks import try_import
from cog_shared.swift_libs.setup import setup_cog


async def setup(bot: Red):
    try:
        setup_cog(bot, "TimedMute", require_version="0.0.2a0")
    except TypeError:
        raise CogLoadError(
            "Your bot is running an outdated version of the shared library this"
            " cog depends on. You can resolve this issue by either running"
            "`[p]swiftlibs reload`, or by restarting your bot."
        )

    try_import("babel")
    from timedmute.shared import translate

    if "TimedRole" not in bot.cogs:
        raise CogLoadError(translate("requires_timedrole"))

    from timedmute.timedmute import TimedMute

    bot.add_cog(TimedMute(bot))
