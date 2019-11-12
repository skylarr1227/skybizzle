from typing import Optional, Union

import discord
from discord.ext import commands
from discord.ext.commands import Bot

from .menu import Menu, action

__all__ = ("confirm", "prompt")


class _ConfirmMenu(Menu):
    async def on_timeout(self):
        await self._handle_post_action(self.DELETE_MESSAGE)

    @action("\N{WHITE HEAVY CHECK MARK}", position=1)
    def yes(self):
        self.kwargs["result"] = True

    @action("\N{CROSS MARK}", position=2)
    def no(self):
        self.kwargs["result"] = False


async def confirm(
    ctx,
    default: bool = False,
    content: str = None,
    embed: discord.Embed = None,
    post_action: str = Menu.DELETE_MESSAGE,
    timeout: Union[int, float] = 30.0,
) -> bool:
    """Prompt a user for confirmation"""
    if getattr(ctx, "assume_yes", False):
        return True

    menu = _ConfirmMenu(
        channel=ctx.channel, bot=ctx.bot, member=ctx.author, content=content, embed=embed
    )
    await menu.prompt(post_action=post_action, timeout=timeout)
    return menu.kwargs.get("result", default)


async def prompt(
    ctx: commands.Context,
    *,
    content: str = None,
    embed: discord.Embed = None,
    delete_messages: bool = False,
    timeout: float = 30.0,
) -> Optional[discord.Message]:
    """Prompt a user for input

    Parameters
    -----------
    ctx: :class:`redbot.core.commands.Context`
        The Red context object
    content: :class:`str`
        The message content to send. If `embed` is given, this is optional
    embed: :class:`discord.Embed`
        The embed to send. If `content` is given, this is optional
    delete_messages: :class:`bool`
        Whether or not the sent messages are deleted when this function returns. If we don't have
        manage message permissions or this is used in a DM, this parameter will have no effect.
    timeout: :class:`float`
        How long to wait for a response from the user

    Returns
    -------
    Optional[:class:`discord.Message`]
        The message that the user sent in response, or :obj:`None` if the prompt timed out.
        The given message may be deleted if ``delete_messages`` is :obj:`True`.
    """
    bot: Bot = ctx.bot
    message_recv = None
    message_sent = await ctx.send(content=content, embed=embed)

    try:
        message_recv = await bot.wait_for(
            "message",
            timeout=timeout,
            check=lambda x: x.author == ctx.author and x.channel == ctx.channel,
        )
    except TimeoutError:
        pass
    finally:
        if (
            delete_messages
            and ctx.guild
            and ctx.channel.permissions_for(ctx.guild.me).manage_messages
        ):
            if message_recv is not None:
                try:
                    await ctx.channel.delete_messages([message_sent, message_recv])
                except discord.HTTPException:
                    pass
            else:
                await message_sent.delete()

    return message_recv
