import json
from datetime import date, timedelta
from random import randint
from typing import Optional, Union, MutableMapping

import aiohttp
import discord
from redbot.core import checks
from redbot.core.utils.chat_formatting import error

from cog_shared.swift_libs.helpers import TimeCache, runtime_data
from misctools import commands
from misctools.shared import translate as translate_, log
from misctools.toolset import Toolset
from swift_i18n import Humanize

BASE_URL = "https://www.xkcd.com"
BASE_IMG_URL = "https://imgs.xkcd.com/comics/"
EXPLAINXKCD_BASE_URL = "https://www.explainxkcd.com/wiki/index.php"

translate = translate_.group("xkcd")
preserved_data = runtime_data("MiscTools")
if "xkcd" not in preserved_data or isinstance(preserved_data.get("xkcd"), list):
    preserved_data["xkcd"] = TimeCache(ttl=timedelta(minutes=30))
COMIC_CACHE: MutableMapping[Union[str, int], "Comic"] = preserved_data["xkcd"]


class NoComic(Exception):
    pass


class XKCD(Toolset, i18n=translate):
    @staticmethod
    async def __build_xkcd_embed(ctx: commands.Context, comic: "Comic"):
        return (
            discord.Embed(
                title=f"#{comic.number} \N{EM DASH} {comic.title}",
                colour=await ctx.embed_colour(),
                url=comic.link,
                description=translate(
                    "description",
                    image=comic.image,
                    explain=comic.explain,
                    date=Humanize(comic.timestamp),
                ),
            ).set_footer(text=comic.alt or discord.Embed.Empty)
            # the image may be an empty string in the case of comic #404
            .set_image(url=comic.image or discord.Embed.Empty)
        )

    @commands.group(invoke_without_command=True)
    @checks.bot_has_permissions(embed_links=True)
    @translate.command("help.root")
    async def xkcd(self, ctx: commands.Context, comic: int = None):
        try:
            comic = await Comic.get(comic)
        except NoComic:
            await ctx.send(error(translate("invalid_comic", comic=comic)))
            return
        else:
            await ctx.send(embed=await self.__build_xkcd_embed(ctx, comic))

    @xkcd.command(name="random")
    @translate.command("help.random")
    async def xkcd_random(self, ctx: commands.Context):
        await ctx.send(embed=await self.__build_xkcd_embed(ctx, await Comic.random()))


class Comic:
    """Wrapper for retrieving xkcd.com comics"""

    def __init__(self, number: int, data: dict):
        self.number = number
        self.link = f"{BASE_URL}/{number}"
        self.explain = f"{EXPLAINXKCD_BASE_URL}/{number}"
        self.title = data.get("safe_title")
        self.alt = data.get("alt")
        self.image = data.get("img", "")

        # keep the original data dict for ease of use
        self.data = data

        if all(x in data for x in ["day", "month", "year"]):
            self.timestamp = date(
                day=int(data.get("day")), month=int(data.get("month")), year=int(data.get("year"))
            )
        else:
            self.timestamp = date(day=1, month=1, year=1970)

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<Comic id={self.number} title={self.title!r}>"

    @classmethod
    async def get(cls, comic_id: Optional[int] = None) -> "Comic":
        """Get the latest or a specified comic"""
        # there is no 404 comic, so special case it to avoid raising a NoComic error
        if comic_id == 404:
            log.debug("special-casing 404 comic")
            return cls(
                404,
                {
                    "num": 404,
                    "safe_title": "Not Found",
                    "alt": "",
                    "img": "",
                    "day": "1",
                    "month": "4",
                    "year": "2008",
                },
            )

        comic_cache_key = comic_id or "_latest"
        if comic_cache_key in COMIC_CACHE:
            log.debug("found comic %r in cache", comic_cache_key)
            return COMIC_CACHE[comic_cache_key]

        async with aiohttp.ClientSession() as session:
            url = [BASE_URL, "info.0.json"]
            if comic_id is not None:
                url.insert(1, str(comic_id))

            url = "/".join(url)
            log.debug("requesting: %r", url)
            async with session.get(url) as response:
                if response.status == 404:
                    raise NoComic

                response.raise_for_status()

                try:
                    data = await response.json()
                except (aiohttp.ContentTypeError, json.JSONDecodeError) as e:
                    log.exception("Failed to decode response", exc_info=e)
                    return cls(-1, {})
                else:
                    comic = cls(data["num"], data)

                log.debug("storing response for %r in cache with key %r", url, comic_cache_key)
                COMIC_CACHE[comic_cache_key] = comic
                # also cache the comic ID if we're retrieving the latest comic
                if comic_cache_key != comic.number:
                    log.debug("additionally %r storing with key %r", url, comic.number)
                    COMIC_CACHE[comic.number] = comic

                return comic

    @classmethod
    async def random(cls) -> "Comic":
        """Get a random comic"""
        latest = await cls.get()
        rnd = randint(1, latest.number)
        # prevent ourselves from choosing 404, since no such comic exists
        while rnd == 404:
            rnd = randint(1, latest.number)
        return await cls.get(rnd)
