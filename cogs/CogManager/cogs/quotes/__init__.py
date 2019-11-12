from redbot.core.bot import Red

from cog_shared.swift_libs.setup import setup_cog


async def setup(bot: Red):
    try:
        setup_cog(bot, "Quotes", require_version="0.0.2a0")
    except TypeError:
        from redbot.core.errors import CogLoadError

        raise CogLoadError(
            "Your bot is running an outdated version of the shared library this"
            " cog depends on. You can resolve this issue by either running"
            "`[p]swiftlibs reload`, or by restarting your bot."
        )

    from quotes.quotes import Quotes

    bot.add_cog(Quotes(bot))
