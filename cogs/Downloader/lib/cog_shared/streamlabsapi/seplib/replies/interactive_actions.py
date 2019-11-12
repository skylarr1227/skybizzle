import asyncio
import copy
from typing import ClassVar, Tuple, List

import discord
from redbot.core.bot import Red

from redbot.core.commands import Context
from redbot.core.utils.menus import start_adding_reactions
from redbot.core.utils.predicates import MessagePredicate, ReactionPredicate


class InteractiveActions(object):
    YES_OR_NO_EMOJIS: ClassVar[Tuple[str, str]] = ("\N{WHITE HEAVY CHECK MARK}", "\N{CROSS MARK}")

    # Create a copy of Red's ReactionPredicate class
    # We need to do this because there's no way to override the Reaction emoji's
    # used with a parameter
    OurReactionPredicate = copy.deepcopy(ReactionPredicate)
    OurReactionPredicate.YES_OR_NO_EMOJIS = YES_OR_NO_EMOJIS

    @staticmethod
    async def yes_or_no_action(ctx: Context, message: str = None, embed: discord.Embed = None, timeout=30) -> bool:

        # We need either a message or an embed object, but not both
        if (message is None and embed is None) or (message is not None and embed is not None):  # pragma: cover
            raise TypeError("Either Message or embed must be set, but not both.")

        can_react = ctx.channel.permissions_for(ctx.me).add_reactions  # pragma: no cover

        # If we can't react, we need respond based on "y/n" strings.
        # Add that indicator to the message or embed.
        if not can_react:  # pragma: no cover
            if message is not None:
                message += "\n\n(y/n)"
            else:
                embed.description += "\n\n(y/n)"

        confirm_message = await ctx.send(content=message, embed=embed)  # pragma: no cover
        if can_react:  # pragma: no cover
            start_adding_reactions(confirm_message, InteractiveActions.YES_OR_NO_EMOJIS, ctx.bot.loop)
            predicate = InteractiveActions.OurReactionPredicate.yes_or_no(confirm_message, ctx.author)
            event = "reaction_add"
        else:  # pragma: no cover
            predicate = MessagePredicate.yes_or_no(ctx)
            event = "message"

        try:  # pragma: no cover
            await ctx.bot.wait_for(event, check=predicate, timeout=timeout)
        except asyncio.TimeoutError:  # pragma: no cover
            await confirm_message.delete()
            return False

        # delete the confirmation message and tell the caller the result of the yes/no.
        await confirm_message.delete()  # pragma: no cover
        return predicate.result  # pragma: no cover

    @staticmethod
    async def wait_for_author_choice(ctx: Context, valid_choices: List[str], timeout: int = 30):

        predicate = MessagePredicate.contained_in(ctx=ctx, user=ctx.author, collection=valid_choices)
        try:
            await ctx.bot.wait_for("message", check=predicate, timeout=timeout)
        except asyncio.TimeoutError:
            return predicate.result

        return predicate.result

    @staticmethod
    async def wait_for_dm_choice(bot: Red, dm: discord.DMChannel, valid_choices: List[str], timeout: int = 30):

        predicate = MessagePredicate.contained_in(channel=dm, ctx=None, user=dm.recipient, collection=valid_choices)
        try:
            await bot.wait_for("message", check=predicate, timeout=timeout)
        except asyncio.TimeoutError:
            return predicate.result

        return predicate.result
