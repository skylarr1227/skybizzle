import asyncio
import hashlib
import types
import warnings

import pytest

from redbot.core import Config
from seplib.tests.utils.functions import simple_coroutine

from seplib.cog import SepCog


class TestSepCog(object):
    def test_bot_set(self, sepcog_empty_cog, red_bot):
        assert isinstance(sepcog_empty_cog.bot, type(red_bot))

    def test_config_created(self, sepcog_empty_cog):
        assert isinstance(sepcog_empty_cog.config, Config)

    def test_config_cog_instance_used(self, sepcog_empty_cog):
        assert sepcog_empty_cog.config.cog_name == sepcog_empty_cog.__class__.__name__

    def test_config_force_registration(self, sepcog_empty_cog):
        assert sepcog_empty_cog.config.force_registration is True

    def test_config_identifier(self, sepcog_empty_cog):
        id_bytes = f"{sepcog_empty_cog.COG_CONFIG_SALT}{sepcog_empty_cog.__class__.__name__}".encode("UTF-8")
        identifier = int(hashlib.sha512(id_bytes).hexdigest(), 16)
        config_hash = str(hash(identifier))
        assert sepcog_empty_cog.config.unique_identifier == config_hash

    def test_init_cache_added(self, sepcog_empty_cog):
        assert len(sepcog_empty_cog._futures) == 1
        _init_cache = sepcog_empty_cog._futures[0]
        assert isinstance(_init_cache, types.CoroutineType)
        assert _init_cache.cr_code.co_name == SepCog._init_cache.__name__

    @pytest.mark.asyncio
    async def test_init_cache_not_implemented(self, sepcog_empty_cog):
        try:
            await SepCog._init_cache(sepcog_empty_cog)
            assert False, "NotImplementedError was not thrown on abstract method."
        except NotImplementedError:
            assert True

    @pytest.mark.asyncio
    async def test_register_configs_not_implemented(self, sepcog_empty_cog, red_config):
        try:
            await SepCog._register_config_entities(sepcog_empty_cog, config=red_config)
            assert False, "NotImplementedError was not thrown on abstract method."
        except NotImplementedError:
            assert True

    @pytest.mark.asyncio
    async def test_add_futures(self, sepcog_empty_cog):
        empty_future_count = 0
        future_name = "empty_future"

        sepcog_empty_cog._add_future(simple_coroutine(future_name))

        for future in sepcog_empty_cog._futures:
            if future.cr_code.co_name == future_name:
                empty_future_count += 1
        assert empty_future_count == 1, "Future not added to futures list correctly."
