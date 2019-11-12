import pytest
from redbot.core.commands import commands

from seplib.cog import SepCog

__all__ = ["sepcog_empty_cog", "red_empty_cog"]


@pytest.fixture()
def red_empty_cog(red_bot):
    class RedCog(commands.Cog):
        def __init__(self, bot):
            super(RedCog, self).__init__()
            self.bot = bot

    cog = RedCog(bot=red_bot)
    cog.bot.cogs["RedCog"] = cog
    return cog


@pytest.fixture()
def sepcog_empty_cog(red_bot):
    class EmptyCog(SepCog, commands.Cog):
        def __init__(self, bot):
            super(EmptyCog, self).__init__(bot=bot)

            self._ensure_futures()

        async def _init_cache(self):
            pass

        def _register_config_entities(self, config):
            pass

    cog = EmptyCog(bot=red_bot)
    cog.bot.cogs["EmptyCog"] = cog
    return cog
