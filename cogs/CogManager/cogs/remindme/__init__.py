from cog_shared.swift_libs.checks import try_import
from cog_shared.swift_libs.setup import setup_cog


async def setup(bot):
    try:
        setup_cog(bot, "RemindMe", require_version="0.0.2a0")
    except TypeError:
        from redbot.core.errors import CogLoadError

        raise CogLoadError(
            "Your bot is running an outdated version of the shared library this"
            " cog depends on. You can resolve this issue by either running"
            "`[p]swiftlibs reload`, or by restarting your bot."
        )

    try_import("babel", "tzlocal")
    from .remindme import RemindMe

    bot.add_cog(RemindMe(bot))
