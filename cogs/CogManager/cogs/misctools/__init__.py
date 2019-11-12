from redbot.core.bot import Red

from cog_shared.swift_libs.checks import try_import
from cog_shared.swift_libs.setup import setup_cog


async def setup(bot: Red):
    try:
        setup_cog(bot, "MiscTools", require_version="0.0.3a0")
    except TypeError:
        from redbot.core.errors import CogLoadError

        raise CogLoadError(
            "Your bot is running an outdated version of the shared library this"
            " cog depends on. You can resolve this issue by either running"
            "`[p]swiftlibs reload`, or by restarting your bot."
        )

    try_import("babel", "tzlocal")
    from misctools.misctools import MiscTools

    cog = MiscTools(bot)
    bot.add_cog(cog)
    try:
        await cog.bootstrap()
    except Exception:
        bot.remove_cog("MiscTools")
        raise
