import asyncio

import pytest

from seplib.tests.utils.functions import coroutine_return, coroutine_exception
from ..utils.queues import EditMemberRoles


class TestEditMemberRoles(object):
    @pytest.mark.asyncio
    async def test_init_sets_cog(self, sepcog_empty_cog):
        emr = EditMemberRoles(cog=sepcog_empty_cog)
        assert emr.cog is sepcog_empty_cog

    @pytest.mark.asyncio
    async def test_init_sets_sleep_interval(self, sepcog_empty_cog):
        emr = EditMemberRoles(cog=sepcog_empty_cog, sleep_interval=4)
        assert emr.sleep_interval == 4

    @pytest.mark.asyncio
    async def test_sepcog_logging_used(self, sepcog_empty_cog):
        emr = EditMemberRoles(cog=sepcog_empty_cog)
        assert emr.logger == sepcog_empty_cog.logger

    @pytest.mark.asyncio
    async def test_creates_new_logger(self, red_empty_cog):
        emr = EditMemberRoles(cog=red_empty_cog)
        assert emr.logger.name == "red.seplib.editmemberroles"

    @pytest.mark.asyncio
    async def test_add_role_appends_modifications(self, monkeypatch, sepcog_empty_cog, discord_member, discord_role):
        key = f"{discord_member.guild.id}|{discord_member.id}"
        monkeypatch.setattr("discord.client.Client.wait_until_ready", coroutine_return(True))
        emr = EditMemberRoles(cog=sepcog_empty_cog)
        await emr.add_role(member=discord_member, role=discord_role)
        assert len(emr._modifications) == 1
        modification = emr._modifications.get(key)
        assert modification is not None
        assert modification.actions[True] == {discord_role}
        assert modification.actions[False] == {None}

    @pytest.mark.asyncio
    async def test_remove_role_appends_modifications(self, monkeypatch, sepcog_empty_cog, discord_member, discord_role):
        key = f"{discord_member.guild.id}|{discord_member.id}"
        monkeypatch.setattr("discord.client.Client.wait_until_ready", coroutine_return(True))
        emr = EditMemberRoles(cog=sepcog_empty_cog)
        await emr.remove_role(member=discord_member, role=discord_role)
        assert len(emr._modifications) == 1
        modification = emr._modifications.get(key)
        assert modification is not None
        assert modification.member == discord_member
        assert modification.actions[True] == set()
        assert modification.actions[False] == {None, discord_role}

    @pytest.mark.asyncio
    async def test_add_role_process_removes_modification(
        self, monkeypatch, sepcog_empty_cog, discord_member, discord_role
    ):
        monkeypatch.setattr("discord.client.Client.wait_until_ready", coroutine_return(True))
        emr = EditMemberRoles(cog=sepcog_empty_cog)
        await emr.add_role(member=discord_member, role=discord_role)
        await asyncio.sleep(emr.sleep_interval)
        assert emr._modifications == {}

    @pytest.mark.asyncio
    async def test_remove_role_process_removes_modification(
        self, monkeypatch, sepcog_empty_cog, discord_member, discord_role
    ):
        monkeypatch.setattr("discord.client.Client.wait_until_ready", coroutine_return(True))
        emr = EditMemberRoles(cog=sepcog_empty_cog)
        await emr.remove_role(member=discord_member, role=discord_role)
        await asyncio.sleep(emr.sleep_interval)
        assert emr._modifications == {}

    @pytest.mark.asyncio
    async def test_add_role_throws_discord_exception(
        self, monkeypatch, sepcog_empty_cog, discord_member, discord_role, disc_http_exception
    ):

        monkeypatch.setattr("discord.client.Client.wait_until_ready", coroutine_return(True))
        monkeypatch.setattr("discord.member.Member.edit", coroutine_exception(disc_http_exception))

        emr = EditMemberRoles(cog=sepcog_empty_cog)
        await emr.remove_role(member=discord_member, role=discord_role)
        await asyncio.sleep(emr.sleep_interval)
