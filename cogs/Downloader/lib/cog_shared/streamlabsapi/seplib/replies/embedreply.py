from typing import Optional, Union

import discord

from ..utils import HexColor


class EmbedReply(object):
    """
    EmbedReply is a very basic helper class for modeling custom embed responses.
    This can be easily subclassed to customize its attributes.
    """

    def __init__(self, message: str, color: Union[HexColor, discord.Colour], emoji: Optional[str] = None):
        self.message = message
        self.color = color
        self.emoji = emoji

        self.content: Optional[str] = None

    def build_message(self) -> str:
        """
        Formats the output message. By default, this will prefix the message with the emoji.
        :return: The message which will, by default, be placed in the Discord embed Description.
        """
        prefix = f"{self.emoji} " if self.emoji is not None else ""
        return f"{prefix}{self.message}"

    def build(self) -> discord.Embed:
        """
        Compiles all of the classes values into a Discord Embed object.
        :return: A discord.py Embed class suitable for sending to a Messageable.
        """
        return discord.Embed(description=self.build_message(), color=self.color)

    async def send(self, target: discord.abc.Messageable):
        """
        Send the content and embed to the supplied Discord Messageable.
        :param target: Discord Messageable object (channel, member, etc).
        :return: None
        """
        return await target.send(content=self.content, embed=self.build())
