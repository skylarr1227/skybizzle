from seplib import setup, SepLib


class TestSeplibCog(object):
    def test_cog_setup(self, red_bot):
        setup(red_bot)
        seplib: SepLib = red_bot.get_cog("SepLib")
        assert seplib.bot is red_bot
