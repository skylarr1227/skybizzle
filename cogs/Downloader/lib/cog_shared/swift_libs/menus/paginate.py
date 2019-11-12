from typing import Sequence, Union, Tuple, Optional

import discord
from discord.ext.commands import Bot

from .menu import Menu, action

__all__ = ("PaginatedMenu",)


class PaginatedMenu(Menu):
    """Paginated variation of :class:`~swift_libs.menus.menu.Menu`"""

    __slots__ = ("pages", "page", "wrap_around")

    def __init__(
        self,
        pages: Sequence[Union[str, discord.Embed, Tuple[str, discord.Embed]]],
        bot: Bot,
        channel: discord.TextChannel,
        member: discord.Member,
        wrap_around: bool = True,
        message: discord.Message = None,
        **kwargs,
    ):
        if "content" in kwargs or "embed" in kwargs:
            raise RuntimeError(
                "Neither 'content' nor 'embed' keyword arguments can be specified for"
                " a paginated menu; use 'pages' instead"
            )

        super().__init__(bot=bot, channel=channel, member=member, message=message, **kwargs)
        self.pages = pages
        self.page = 0
        self.wrap_around = wrap_around

    @property
    def current_page(self):
        return self.pages[self.page]

    @property
    def content(self) -> Optional[str]:
        if isinstance(self.current_page, tuple):
            return next((x for x in self.current_page if isinstance(x, str)), None)
        else:
            return self.current_page if isinstance(self.current_page, str) else None

    @property
    def embed(self) -> Optional[discord.Embed]:
        if isinstance(self.current_page, tuple):
            return next((x for x in self.current_page if isinstance(x, discord.Embed)), None)
        else:
            return self.current_page if isinstance(self.current_page, discord.Embed) else None

    @action("\N{LEFTWARDS BLACK ARROW}", position=-99, continue_after_use=True)
    async def backwards(self, *_, **__):
        if self.page <= 0:
            if self.wrap_around:
                self.page = len(self.pages) - 1
            else:
                return
        else:
            self.page -= 1
        await self.update_message()

    @action("\N{BLACK RIGHTWARDS ARROW}", position=99, continue_after_use=True)
    async def forwards(self):
        if self.page >= len(self.pages) - 1:
            if self.wrap_around:
                self.page = 0
            else:
                return
        else:
            self.page += 1
        await self.update_message()
