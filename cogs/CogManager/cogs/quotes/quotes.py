from random import randint

import discord
from redbot.core import checks, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import warning

from cog_shared.swift_libs.formatting import tick
from cog_shared.swift_libs.menus import confirm
from quotes.quote import Quote, conf, translate


@translate.cog("help.cog_class")
class Quotes(commands.Cog):
    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = conf
        Quote.bot = self.bot

    @commands.group(name="quote", aliases=["quotes"], invoke_without_command=True)
    @commands.guild_only()
    @translate.command("help.root")
    async def quote(self, ctx: commands.Context, quote: Quote = None):
        if quote is None:
            quotes = len(await self.config.guild(ctx.guild).quotes())
            if not quotes:
                await ctx.send_help()
                return
            quote = await Quote.get(ctx.guild, randint(1, quotes))

        await ctx.send(embed=quote.embed)

    @quote.command(hidden=True, name="clearall")
    @checks.guildowner()
    @translate.command("help.clearall")
    async def quote_clearall(self, ctx: commands.Context):
        if not await confirm(ctx, content=translate("reset_confirmation")):
            await ctx.send(translate("op_cancelled"))
            return

        await self.config.guild(ctx.guild).quotes.set([])
        await ctx.tick()

    @quote.command(name="add")
    @translate.command("help.add")
    async def quote_add(self, ctx: commands.Context, *, message: str):
        quote = await Quote.create(message, ctx.author, ctx.author)
        await ctx.send(tick(translate("quote_added")), embed=quote.embed)

    @quote.command(name="message")
    @translate.command("help.message")
    async def quote_message(
        self, ctx: commands.Context, message: int, channel: discord.TextChannel = None
    ):
        channel = channel or ctx.channel
        try:
            message = await channel.get_message(message)
        except discord.NotFound:
            await ctx.send(warning(translate("message_not_found")))
        except discord.Forbidden:
            await ctx.send(warning(translate("message_forbidden")))
        else:
            quote = await Quote.create(message.content, ctx.author, message.author)
            await ctx.send(tick(translate("quote_added")), embed=quote.embed)

    @quote.command(name="author", aliases=["attribute"])
    @translate.command("help.attribute")
    async def edit_author(self, ctx: commands.Context, quote: Quote, *, author: discord.Member):
        await quote.ensure_can_modify(ctx.author)

        quote.message_author = author
        await quote.save()
        await ctx.send(tick(translate("quote_attributed", id=int(quote), member=str(author))))

    @quote.command(name="remove", aliases=["rm", "delete"])
    @translate.command("help.remove")
    async def quote_remove(self, ctx: commands.Context, quote: Quote):
        await quote.ensure_can_modify(ctx.author)

        if await confirm(ctx, content=warning(translate("delete_confirmation"))):
            await quote.delete()
            await ctx.send(tick(translate("quote_deleted")))
        else:
            await ctx.send(translate("op_cancelled"))
