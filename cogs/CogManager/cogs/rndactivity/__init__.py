from redbot.core.bot import Red

from cog_shared.swift_libs.setup import setup_cog
from cog_shared.swift_libs.checks import try_import


async def setup(bot: Red):
    try:
        setup_cog(bot, "RNDActivity", require_version="0.0.3a0")
    except TypeError:
        from redbot.core.errors import CogLoadError

        raise CogLoadError(
            "Your bot is running an outdated version of the shared library this"
            " cog depends on. You can resolve this issue by either running"
            "`[p]swiftlibs reload`, or by restarting your bot."
        )

    try_import("babel")
    from rndactivity.rndactivity import RNDActivity

    bot.add_cog(RNDActivity(bot))
