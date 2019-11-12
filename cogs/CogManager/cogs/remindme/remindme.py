import asyncio
import logging
from datetime import datetime
from textwrap import shorten

import discord
from redbot.core import Config, commands
from redbot.core.bot import Red
from tzlocal import get_localzone

from cog_shared.swift_libs.formatting import tick
from cog_shared.swift_libs.helpers import chunks
from cog_shared.swift_libs.menus import PaginatedMenu, confirm
from cog_shared.swift_libs.time import FutureTime
from cog_shared.swift_libs.i18n import Translator
from swift_i18n import Humanize
from .reminder import Reminder

translate = Translator(__file__)
log = logging.getLogger("red.remindme")


@translate.cog("help.cog_class")
class RemindMe(commands.Cog):
    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=2424356456, force_registration=True)
        self.config.register_user(reminders=[])
        Reminder.cfg = self.config
        Reminder.bot = self.bot
        self.task = self.bot.loop.create_task(self.reminder_handler())

    def cog_unload(self):
        self.task.cancel()

    async def reminder_handler(self):
        await self.bot.wait_until_ready()
        while True:
            async for reminder in Reminder.all_reminders():
                if not reminder.is_due(True):
                    continue

                try:
                    await reminder.send_reminder()
                except discord.Forbidden:
                    log.warning(
                        "Could not send a reminder message to %r; did they block us?", reminder.user
                    )
                except discord.HTTPException as e:
                    log.exception(
                        "Failed to send reminder message to %r", reminder.user, exc_info=e
                    )
                except Exception as e:
                    log.exception("Failed to send reminder", exc_info=e)
                finally:
                    await reminder.remove()

            await asyncio.sleep(60 * 3)

    @commands.group(invoke_without_command=True, aliases=["remind", "reminder"])
    @translate.command("help.root")
    async def remindme(self, ctx: commands.Context, in_time: str, *, to: str):
        if len(to) > 1000:
            await ctx.send(translate("content_too_long"))
            return

        in_time = FutureTime.get_seconds(in_time)
        if in_time is None or in_time < 60:
            raise commands.BadArgument(translate("invalid_time"))

        reminder = await Reminder.create(ctx.author, to, in_time)
        if await ctx.embed_requested():
            embed = discord.Embed(
                colour=await ctx.embed_colour(),
                description=reminder.message,
                title=translate("reminder_created"),
                timestamp=reminder.due_on,
            )
            embed.set_footer(text=translate("will_send_on"))
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                tick(
                    translate(
                        "reminder_set",
                        date=Humanize(reminder.due_on, format="long", tzinfo=get_localzone()),
                    )
                )
            )

    @remindme.command()
    @translate.command("help.clear")
    async def clear(self, ctx: commands.Context):
        if await confirm(ctx, content=translate("confirm_clear")):
            await self.config.user(ctx.author).reminders.set([])
            await ctx.send(tick(translate("reminders_cleared")))
        else:
            await ctx.send(translate("ok_then"))

    @remindme.command()
    @translate.command("help.list")
    async def list(self, ctx: commands.Context):
        reminders = await self.config.user(ctx.author).reminders()
        if not reminders:
            await ctx.send(translate("no_set_reminders", prefix=ctx.prefix))
            return

        pages = list(chunks(reminders, 5))
        page_count = len(pages)
        colour = await ctx.embed_colour()
        # noinspection PyUnresolvedReferences
        for page in pages.copy():
            index = pages.index(page)
            embed = discord.Embed(colour=colour)
            embed.set_author(
                name=translate("set_reminders", user=ctx.author),
                icon_url=ctx.author.avatar_url_as(format="png"),
            )
            embed.set_footer(text=translate("page", total=page_count, current=index + 1))

            for reminder in page:
                remind_on = datetime.utcfromtimestamp(reminder["remind_on"])
                embed.add_field(
                    name=translate(
                        "reminder_title",
                        id=(index * 5) + (page.index(reminder) + 1),
                        delta=Humanize(remind_on - datetime.utcnow(), add_direction=True),
                    ),
                    value=shorten(
                        reminder["message"], width=700, placeholder=" \N{HORIZONTAL ELLIPSIS}"
                    ),
                    inline=False,
                )

            pages[index] = embed

        await PaginatedMenu(
            pages=pages, bot=self.bot, member=ctx.author, channel=ctx.channel
        ).prompt()

    @remindme.command()
    @translate.command("help.remove")
    async def remove(self, ctx: commands.Context, reminder: int):
        try:
            reminder = Reminder(
                ctx.author, (await self.config.user(ctx.author).reminders())[reminder - 1]
            )
        except IndexError:
            await ctx.send(translate("no_such_reminder", prefix=ctx.prefix))
            return

        if not await confirm(
            ctx,
            content=translate("remove_confirmation"),
            embed=discord.Embed(description=reminder.message, timestamp=reminder.due_on).set_footer(
                text=translate("due_on")
            ),
        ):
            await ctx.send(translate("ok_then"))
            return

        await reminder.remove()
        await ctx.tick()
