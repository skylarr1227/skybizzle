import pytest

from seplib.replies import EmbedReply, ErrorReply, SuccessReply
from seplib.tests.utils.functions import coroutine_return_args
from seplib.tests.utils.strings import random_string
from seplib.utils import HexColor


async def base_content_send(patch, ctx, reply_type, **kwargs):

    embed_reply = reply_type(message="", **kwargs)
    check_embed = embed_reply.build()
    patch.setattr("discord.abc.Messageable.send", coroutine_return_args())

    send_result = await embed_reply.send(ctx)
    assert send_result["kwargs"].get("content", object()) is None
    embed_send = send_result["kwargs"].get("embed", object())
    assert isinstance(embed_send, type(check_embed))
    assert embed_send.color == check_embed.color
    assert embed_send.description == check_embed.description


class TestEmbedReply(object):
    def test_embed_sets_message(self):
        message = random_string()
        embed_reply = EmbedReply(message=message, color=HexColor.success())
        assert embed_reply.message == message

    def test_embed_sets_color(self):
        color = HexColor.rebecca_purple()
        embed_reply = EmbedReply(message="", color=color)
        assert embed_reply.color == color

    def test_embed_sets_emoji(self):
        emoji = "\N{PILE OF POO}"
        embed_reply = EmbedReply(message="", color=HexColor.success(), emoji=emoji)
        assert embed_reply.emoji == emoji

    def test_embed_content_is_none(self):
        embed_reply = EmbedReply(message="", color=HexColor.success())
        assert embed_reply.content is None

    def test_embed_build_message_no_emoji(self):
        message = random_string()
        expected = f"{message}"
        embed_reply = EmbedReply(message=message, color=HexColor.success(), emoji=None)
        assert embed_reply.build_message() == expected

    def test_embed_build_message_emoji(self):
        emoji = "\N{PILE OF POO}"
        message = random_string()
        expected = f"{emoji} {message}"
        embed_reply = EmbedReply(message=message, color=HexColor.success(), emoji=emoji)
        assert embed_reply.build_message() == expected

    def test_embed_build_embed_no_emoji(self):
        color = HexColor.rebecca_purple()
        message = random_string()
        embed_reply = EmbedReply(message=message, color=color, emoji=None)

        embed = embed_reply.build()
        assert embed.color == color
        assert embed.description == message

    def test_embed_build_embed_emoji(self):
        emoji = "\N{PILE OF POO}"
        color = HexColor.rebecca_purple()
        message = random_string()
        expected = f"{emoji} {message}"
        embed_reply = EmbedReply(message=message, color=color, emoji=emoji)

        embed = embed_reply.build()
        assert embed.color == color
        assert embed.description == expected

    @pytest.mark.asyncio
    async def test_embed_sends_content(self, monkeypatch, red_context):
        await base_content_send(patch=monkeypatch, ctx=red_context, reply_type=EmbedReply, color=HexColor.purple())


class TestErrorReply(object):
    def test_error_sets_emoji(self):
        error_reply = ErrorReply(message="")
        assert error_reply.emoji == "\N{CROSS MARK}"

    def test_error_sets_color(self):
        error_reply = ErrorReply(message="")
        assert error_reply.color == HexColor.red()

    @pytest.mark.asyncio
    async def test_error_reply_send(self, monkeypatch, red_context):
        await base_content_send(patch=monkeypatch, ctx=red_context, reply_type=ErrorReply)


class TestSuccessReply(object):
    def test_success_sets_emoji(self):
        success_reply = SuccessReply(message="")
        assert success_reply.emoji == "\N{WHITE HEAVY CHECK MARK}"

    def test_success_sets_color(self):
        success_reply = SuccessReply(message="")
        assert success_reply.color == HexColor.success()

    @pytest.mark.asyncio
    async def test_error_reply_send(self, monkeypatch, red_context):
        await base_content_send(patch=monkeypatch, ctx=red_context, reply_type=SuccessReply)
