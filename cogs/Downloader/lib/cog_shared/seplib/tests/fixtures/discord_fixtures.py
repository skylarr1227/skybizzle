import discord
import pytest

from seplib.tests.utils.classes import simple_class_factory

__all__ = ["disc_http_exception"]


@pytest.fixture()
def disc_http_exception():
    response = simple_class_factory(status=401, reason="")
    return discord.HTTPException(message="", response=response)
