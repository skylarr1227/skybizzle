import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Coroutine, List

from redbot.core import Config, commands
from redbot.core.bot import Red

__all__ = ["SepCog"]


class SepCog(commands.Cog):
    """
    Base cog which provides common functionality between multiple different cogs, such as
    initializing config, defining logging, and and other utilities.
    """

    COG_CONFIG_SALT = "twitch.tv/seputaes"

    def __init__(self, bot: Red):
        super(SepCog, self).__init__()
        self.bot = bot

        self.config: Config = self._setup_config()

        self.logger = logging.getLogger(f"red.sep-cogs.{self.__class__.__name__.lower()}")
        self.logger.setLevel(logging.INFO)

        self._futures: List[Coroutine] = []
        self._add_future(self._init_cache())

    @abstractmethod
    async def _init_cache(self):
        """
        Implementation in each Cog uses this to get any data that it needs from the database
        and load it into memory/convert into a better structure at the time of cog load.
        :return: None
        """
        raise NotImplementedError("Cannot call this method directly on the abstract class.")

    @abstractmethod
    def _register_config_entities(self, config: Config):
        """
        Takes a Red config instance and registers the configuration entities needed before
        initializing them to the Cog instance.

        Implementing cogs will all have unique config entities and needs.
        :param config: Red config entity.
        :return: None
        """
        raise NotImplementedError("Cannot call this method directly on the abstract class.")

    def _setup_config(self) -> Config:
        """
        Generates a Red config which is unique to the cog.
        :return: Red config.
        """
        id_bytes = f"{self.COG_CONFIG_SALT}{self.__class__.__name__}".encode("UTF-8")
        identifier = int(hashlib.sha512(id_bytes).hexdigest(), 16)

        config = Config.get_conf(cog_instance=self, identifier=identifier, force_registration=True)
        self._register_config_entities(config)
        return config

    def _add_future(self, coroutine: Coroutine):
        """
        Used during cog init to queue up futures which should be ensured as the last step of cog
        loading.
        :param coroutine: Coroutine to be added with ensure_future.
        :return: None
        """
        self._futures.append(coroutine)

    def _ensure_futures(self):
        for coroutine in self._futures:
            asyncio.ensure_future(coroutine)
