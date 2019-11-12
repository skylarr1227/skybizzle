import pytest

from seplib.tests.utils.functions import coroutine_return, coroutine_exception
from seplib.tests.utils.strings import random_string
from seplib.utils import ContextWrapper


class TestContextWrapper(object):
    def test_context_set(self, red_context):
        wrapper = ContextWrapper(red_context)
        assert wrapper.ctx is red_context

    @pytest.mark.asyncio
    async def test_cross_success(self, monkeypatch, red_context):
        monkeypatch.setattr("discord.message.Message.add_reaction", coroutine_return(None))

        wrapper = ContextWrapper(red_context)
        assert (await wrapper.cross()) is True

    @pytest.mark.asyncio
    async def test_cross_discord_error_returns_false(self, monkeypatch, red_context, disc_http_exception):
        monkeypatch.setattr("discord.message.Message.add_reaction", coroutine_exception(disc_http_exception))
        wrapper = ContextWrapper(red_context)

        assert (await wrapper.cross()) is False

    @pytest.mark.asyncio
    async def test_cross_raises_other_exceptions(self, monkeypatch, red_context):
        class NewBaseException(BaseException):
            pass

        message = random_string()
        exception = NewBaseException(message)

        monkeypatch.setattr("discord.message.Message.add_reaction", coroutine_exception(exception))

        wrapper = ContextWrapper(red_context)
        try:
            await wrapper.cross()
            assert False, "Cross method swallowed non-HTTP exceptions"
        except BaseException as e:
            assert type(e) is NewBaseException
            assert e.args[0] == message
