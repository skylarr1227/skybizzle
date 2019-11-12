import discord

from redbot.core.commands import Context


class ContextWrapper(object):
    """
    Wrapper around Red's Context class in order to extend it and add additional
    functionality.
    """

    __CROSS = "\N{CROSS MARK}"

    def __init__(self, ctx: Context):
        self.ctx = ctx

    async def cross(self) -> bool:
        """
        Add a cross mark reaction (failure) to the command message.
        :return: Returns true if adding the reaction succeeded.
        """
        try:
            await self.ctx.message.add_reaction(self.__CROSS)
            return True
        except discord.HTTPException:
            return False
