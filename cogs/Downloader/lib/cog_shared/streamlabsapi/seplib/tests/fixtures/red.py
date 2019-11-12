import hashlib

import pytest

from redbot.core.drivers.red_base import BaseDriver

from redbot.core import Config

from redbot.core.bot import Red
from seplib.tests.utils.strings import random_string

__all__ = [
    "red_bot",
    "red_base_driver",
    "red_config",
    "red_context",
    "discord_message",
    "discord_connection",
    "discord_messageable",
    "discord_guild",
    "discord_member",
    "discord_user",
    "discord_role",
    "discord_dm_channel",
    "message_predicate",
]


@pytest.fixture()
def red_bot():
    from redbot.core.cli import parse_cli_flags

    cli_flags = parse_cli_flags([])
    description = "seplib pytest"
    red = Red(cli_flags=cli_flags, description=description)
    yield red


@pytest.fixture()
def red_base_driver():
    id_ = int(hashlib.sha1("Pytest Cog".encode("UTF-8")).hexdigest(), 16)
    return BaseDriver(cog_name="Pytest Cog", identifier=id_)


@pytest.fixture()
def red_config(red_base_driver):
    return Config(
        cog_name=red_base_driver.cog_name,
        unique_identifier=red_base_driver.unique_cog_identifier,
        driver=red_base_driver,
    )


@pytest.fixture()
def discord_connection():
    class ConnectionState(object):
        http = None

        def store_user(self, author):
            return author

    return ConnectionState()


@pytest.fixture()
def discord_messageable():
    from discord.abc import Messageable

    class M(Messageable):
        async def _get_channel(self):
            return self

    return M()


@pytest.fixture()
def discord_guild(discord_connection):
    from discord import Guild

    return Guild(data={"id": 1, "name": "FakeGuild"}, state=discord_connection)


@pytest.fixture()
def discord_role(discord_connection, discord_guild):
    from discord import Role

    return Role(data={"id": 1, "name": "FakeRole"}, guild=discord_guild, state=discord_connection)


@pytest.fixture()
def discord_user(discord_connection):
    from discord import User

    return User(data={"id": 1, "username": "FakeUser", "discriminator": "0001", "avatar": ""}, state=discord_connection)


@pytest.fixture()
def discord_member(discord_connection, discord_guild, discord_user):
    from discord import Member

    member = Member(data={"id": 1, "user": discord_user, "roles": []}, state=discord_connection, guild=discord_guild)
    return member


@pytest.fixture()
def discord_message(discord_messageable, discord_connection):
    from discord import Message

    return Message(channel=discord_messageable, data={"id": 1, "author": "foo"}, state=discord_connection)


@pytest.fixture()
def discord_dm_channel(discord_connection):
    from discord import DMChannel

    return DMChannel(data={"id": 1, "recipients": [None]}, state=discord_connection, me=None)


@pytest.fixture()
def red_context(discord_message, red_bot):
    from redbot.core.commands import Context

    return Context(prefix="!", message=discord_message, bot=red_bot)


@pytest.fixture()
def message_predicate():
    from redbot.core.utils.predicates import MessagePredicate

    p = MessagePredicate(predicate=None)
    p.result = random_string()
    return p
