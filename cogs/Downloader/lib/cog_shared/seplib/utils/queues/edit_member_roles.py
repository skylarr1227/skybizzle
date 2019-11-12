import asyncio
import logging
from typing import Dict, Optional, Set

import discord

from redbot.core.bot import Red
from redbot.core.commands import commands

__all__ = ["EditMemberRoles", "RoleModification"]


class EditMemberRoles(object):
    def __init__(self, cog: commands.Cog, sleep_interval: int = 2):

        self._queue = asyncio.Queue()
        self._modifications: Dict[str, RoleModification] = {}
        self.sleep_interval = sleep_interval
        self.cog = cog

        cog_logger = getattr(cog, "logger", None)
        if not cog_logger:
            self.logger = logging.getLogger(f"red.seplib.{self.__class__.__name__.lower()}")
            self.logger.setLevel(logging.INFO)
        else:
            self.logger = cog_logger

        asyncio.ensure_future(self._process_add_remove_actions())

    async def _process_add_remove_actions(self):
        """
        While the cog is loaded, runs in a loop to check if any role add/remove actions have been added to an
        asyncio queue. If they have, gets the modifications and modifies the member with the result of the
        add/remove modification.
        :return: None
        """

        bot: Red = getattr(self.cog, "bot", None)
        if not bot:  # pragma: no cover
            self.logger.error("There was no Red bot instance on the cog! Cannot proceed!")
            return

        await bot.wait_until_ready()

        while self.cog == bot.get_cog(self.cog.__class__.__name__):

            key = await self._queue.get()

            mod: Optional[RoleModification] = self._modifications.pop(key, None)
            if mod:
                curr_roles = set(mod.member.roles)
                add = mod.actions[True]
                remove = mod.actions[False]

                result = (curr_roles | add) - remove
                try:
                    await mod.member.edit(roles=result)
                    self.logger.info(  # pragma: no cover
                        f"Edited roles on member: {mod.member} | "
                        f"Guild: {mod.member.guild}|{mod.member.guild.id} | "
                        f"Added: {add} | Removed: {remove - {mod.member.guild.default_role}}"
                    )
                except discord.HTTPException as de:  # pragma: no cover
                    self.logger.error(
                        "Discord Error while editing roles."
                        f"Guild: {mod.member.guild}|{mod.member.guild.id} | "
                        f"Error: {de}"
                    )
                finally:
                    self._queue.task_done()
            await asyncio.sleep(self.sleep_interval)

    async def _add_modification(self, member: discord.Member, role: discord.Role, action: bool) -> None:
        """
        Queues up a role modification.
        :param member: Discord Member
        :param role: Discord Role
        :param action: True/False for Add/Remove
        :return:
        """
        key = f"{member.guild.id}|{member.id}"
        mod = self._modifications.get(key)

        if not mod:
            mod = RoleModification(member=member, actions={True: set(), False: {member.guild.default_role}})
        mod.actions[action].add(role)
        mod.actions[not action] -= {role}

        self._modifications[key] = mod
        await self._queue.put(key)

    async def add_role(self, member: discord.Member, role: discord.Role) -> None:
        """
        Queues up an add role modification on the member.
        :param member: Discord Member
        :param role: Discord Role
        :return: None
        """
        return await self._add_modification(member=member, role=role, action=True)

    async def remove_role(self, member: discord.Member, role: discord.Role):
        """
        Queues up a remove role modification on the member.
        :param member: Discord member
        :param role: Discord Role
        :return: None
        """
        return await self._add_modification(member=member, role=role, action=False)


class RoleModification(object):
    """
    Container object for a specific member and the queued up role add/remove actions.
    """

    def __init__(self, member: discord.Member, actions: Dict[bool, Set]) -> None:
        self.member = member
        self.actions = actions
