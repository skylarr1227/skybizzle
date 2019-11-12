import asyncio

import pytest
from redbot.core.utils.predicates import MessagePredicate

from seplib.replies import InteractiveActions, SuccessReply
from seplib.tests.utils.functions import (
    coroutine_exception,
    coroutine_return_args,
    coroutine_return_modified_args,
    simple_return_function,
)


class TestInteractiveActions(object):
    @pytest.mark.asyncio
    async def test_message_xor_embed_provided(self, red_context):

        try:
            await InteractiveActions.yes_or_no_action(ctx=red_context, message=None, embed=None)
            assert False, "TypeError should have been raised, but wasn't"
        except TypeError:
            assert True

        try:
            embed = SuccessReply(message="").build()
            await InteractiveActions.yes_or_no_action(ctx=red_context, message="", embed=embed)
            assert False, "TypeError should have been raised, but wasn't"
        except TypeError:
            assert True

    @pytest.mark.asyncio
    async def test_author_choice_predicate_timeout_exception(self, red_context, monkeypatch):
        exception = asyncio.TimeoutError("Our Exception")
        choices = []
        monkeypatch.setattr("redbot.core.bot.Red.wait_for", coroutine_exception(exception))

        result = await InteractiveActions.wait_for_author_choice(ctx=red_context, valid_choices=choices)
        assert result is None

    @pytest.mark.asyncio
    async def test_author_choice_predicate_other_exception(self, monkeypatch, red_context, disc_http_exception):
        choices = []
        monkeypatch.setattr("redbot.core.bot.Red.wait_for", coroutine_exception(disc_http_exception))

        try:
            await InteractiveActions.wait_for_author_choice(ctx=red_context, valid_choices=choices)
            assert False, "Method caught exception it was not supposed to."
        except type(disc_http_exception):
            assert True

    @pytest.mark.asyncio
    async def test_author_choice_predicate_valid(self, monkeypatch, red_context, message_predicate):
        modified_dict, coroutine = coroutine_return_modified_args()
        monkeypatch.setattr(
            "redbot.core.utils.predicates.MessagePredicate.contained_in",
            simple_return_function(return_value=message_predicate),
        )
        monkeypatch.setattr("redbot.core.bot.Red.wait_for", coroutine)

        await InteractiveActions.wait_for_author_choice(ctx=red_context, valid_choices=["1", "2", "3"])
        predicate = modified_dict.get("kwargs", {}).get("check")
        assert predicate.result == message_predicate.result

    @pytest.mark.asyncio
    async def test_dm_choice_predicate_timeout_exception(self, monkeypatch, red_context, discord_dm_channel):
        exception = asyncio.TimeoutError("Our Exception")
        monkeypatch.setattr("redbot.core.bot.Red.wait_for", coroutine_exception(exception))

        result = await InteractiveActions.wait_for_dm_choice(
            bot=red_context.bot, dm=discord_dm_channel, valid_choices=[]
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_dm_choice_predicate_other_exception(
        self, monkeypatch, red_context, discord_dm_channel, disc_http_exception
    ):
        monkeypatch.setattr("redbot.core.bot.Red.wait_for", coroutine_exception(disc_http_exception))

        try:
            await InteractiveActions.wait_for_dm_choice(dm=discord_dm_channel, valid_choices=[], bot=red_context.bot)
            assert False, "Method caught exception it was not supposed to."
        except type(disc_http_exception):
            assert True

    @pytest.mark.asyncio
    async def test_dm_choice_predicate_valid_(self, monkeypatch, red_context, discord_dm_channel, message_predicate):
        modified_dict, coroutine = coroutine_return_modified_args()
        monkeypatch.setattr(
            "redbot.core.utils.predicates.MessagePredicate.contained_in",
            simple_return_function(return_value=message_predicate),
        )
        monkeypatch.setattr("redbot.core.bot.Red.wait_for", coroutine)

        await InteractiveActions.wait_for_dm_choice(
            bot=red_context.bot, dm=discord_dm_channel, valid_choices=["1", "2", "3"]
        )
        predicate = modified_dict.get("kwargs", {}).get("check")
        assert predicate.result == message_predicate.result
