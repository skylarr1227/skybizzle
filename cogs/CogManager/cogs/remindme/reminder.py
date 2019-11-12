from datetime import datetime, timedelta
from time import time
from typing import AsyncIterable

import discord
from redbot.core.bot import Red
from redbot.core.config import Config
from tzlocal import get_localzone
from swift_i18n import Humanize


class Reminder:
    cfg: Config
    bot: Red

    def __init__(self, user: discord.User, data: dict):
        self.user = user
        self._data = data

    @classmethod
    async def all_reminders(cls, user: discord.User = None) -> AsyncIterable["Reminder"]:
        if user is None:
            users = await cls.cfg.all_users()
        else:
            users = {user.id: await cls.cfg.user(user).all()}

        for uid, data in users.items():
            for reminder in data.get("reminders", []):
                u = cls.bot.get_user(int(uid))
                if not u:
                    continue
                yield cls(user=u, data=reminder)

    @classmethod
    async def create(cls, user: discord.User, message: str, due_in: float) -> "Reminder":
        now = time()
        reminder = cls(user, {"message": message, "set_on": now, "remind_on": now + due_in})
        await reminder.save()
        return reminder

    async def save(self):
        async with self.cfg.user(self.user).reminders() as reminders:
            if self._data not in reminders:
                reminders.append(self._data)

    async def remove(self):
        async with self.cfg.user(self.user).reminders() as reminders:
            if self._data in reminders:
                reminders.remove(self._data)

    @property
    def reminder_embed(self):
        from .remindme import translate

        return discord.Embed(
            title=translate("reminder_header"),
            timestamp=self.set_on,
            description=self.message,
            colour=self.bot.color,
        ).set_footer(text=translate("reminder_set_on"))

    @property
    def reminder_text(self):
        from .remindme import translate

        return translate(
            "reminder_message",
            set_on=Humanize(self.set_on, format="long", tzinfo=get_localzone()),
            message=self.message,
        )

    async def send_reminder(self):
        if self.user.dm_channel is None:
            await self.user.create_dm()

        if await self.bot.embed_requested(self.user.dm_channel, self.user):
            await self.user.send(embed=self.reminder_embed)
        else:
            await self.user.send(content=self.reminder_text)

    @property
    def message(self):
        return self._data["message"]

    @property
    def set_on(self) -> datetime:
        return datetime.utcfromtimestamp(self._data["set_on"])

    @property
    def due_on(self) -> datetime:
        return datetime.utcfromtimestamp(self._data["remind_on"])

    def is_due(self, lenient: bool = False):
        if datetime.utcnow() > self.due_on:
            return True
        if lenient:
            return datetime.utcnow() + timedelta(minutes=1) > self.due_on
        return False
