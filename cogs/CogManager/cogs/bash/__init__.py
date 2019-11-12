from .bash import Bash

def setup(bot):
    bot.add_cog(Bash(bot))
