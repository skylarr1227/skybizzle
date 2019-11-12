import asyncio
import warnings
from contextlib import suppress
from functools import partial
from typing import Optional, Union, List, Callable, ClassVar, Tuple, Awaitable

import discord
from discord.ext.commands import Bot

from .._internal import log

__all__ = ("PostAction", "action", "Action", "Menu")


class PostAction:
    def __getattr__(self, item):
        warnings.warn(
            f"PostAction.{item} is deprecated; use Menu.{item} instead",
            stacklevel=2,
            category=DeprecationWarning,
        )
        return getattr(Menu, item)


PostAction = PostAction()


def action(
    emoji: Union[str, discord.Emoji],
    *,
    position: int = None,
    continue_after_use: bool = False,
    post_action: str = None,
) -> Callable[[Callable[[], None]], "Action"]:
    """Define a new menu action

    Parameters
    ----------
    emoji: Union[:class:`str`, :class:`discord.Emoji`]
        The emoji to associate this action to
    position: :class:`int`
        The position this reaction should be placed in compared to all other reactions
    continue_after_use: :class:`bool`
        If this is :obj:`True`, the menu will not stop execution when this action
        is used. This is mostly useful for things such as pagination buttons.
    post_action: :class:`str`
        The action to perform when this action is executed. This will only ever be used
        if ``continue_after_use`` is :obj:`True`.
    """

    def wrapper(func):
        return Action(func, emoji, position, continue_after_use, post_action or Menu.NO_ACTION)

    return wrapper


class Action:
    """Menu action button

    See :func:`action` for usage.
    """

    def __init__(
        self,
        func: Callable,
        emoji: Union[str, discord.Emoji],
        position: int,
        continue_after_use: bool,
        post_action: str,
    ):
        self.func = func
        self.emoji = emoji
        self.position = position
        self.continue_after_use = continue_after_use
        self.post_action = post_action

    def __repr__(self):
        return f"<Action func={self.func!r} emoji={self.emoji!r} position={self.position!r}>"

    def __get__(self, instance, owner):
        if instance is not None:
            return partial(discord.utils.maybe_coroutine, self.func, instance)
        return self

    def __call__(self, *args, **kwargs) -> Awaitable[None]:
        return discord.utils.maybe_coroutine(self.func, *args, **kwargs)


class Menu:
    """Simple yet powerful reaction-based menu utility

    All given keyword arguments not listed below will be stored in a class variable called `kwargs`,
    to more easily allow for advanced menu setups.

    Example
    -------
    .. code-block:: python

        from swift_libs import Menu, action

        class MyMenu(Menu):
            # emojis may either be str emoji characters (e.g. "\N{WAVING HAND SIGN}")
            # or custom discord emojis
            @action(emoji)
            def my_action(self):
                # do stuff

        async def my_command(ctx):
            await MyMenu(
                channel=ctx.channel,
                bot=ctx.bot,
                member=ctx.author,
                content="my message content",
            ).prompt()

    Arguments
    ---------
    bot: :class:`discord.ext.commands.Bot`
        The bot instance to use
    channel: class:`discord.TextChannel`
        The text channel the associated menu message should be sent in
    member: :class:`discord.Member`
        The member to listen to reactions from
    content: :class:`str`
        The message content to use when sending the associated menu message.
        Either this and/or ``embed`` must be specified, or overridden in the class as a property.
    embed: :class:`discord.Embed`
        The message embed to use when sending the associated menu message.
        Either this and/or ``content`` must be specified, or overridden in the class as a property.
    """

    __slots__ = ("bot", "channel", "member", "message", "kwargs", "content", "embed", "_react_task")
    actions: ClassVar[Tuple[Action, ...]] = ()

    NO_ACTION = "none"
    CLEAR_REACTIONS = "clear"
    DELETE_MESSAGE = "delete"

    def __init_subclass__(cls):
        # We want to overwrite actions that use the same emoji as another (such as replacing
        # pagination buttons from PaginatedMenu), but if those override actions don't specify
        # a position, use the position from the action we're overriding
        actions = {x.emoji: (x, x.position or 0) for x in cls.actions}
        actions.update(
            {
                x.emoji: (
                    x,
                    actions.get(x.emoji, (..., 0))[1] if x.position is None else x.position,
                )
                for x in cls.__dict__.values()
                if isinstance(x, Action)
            }
        )
        actions = list(actions.values())
        cls.actions = tuple([x[0] for x in sorted(actions, key=lambda x: x[1])])

    def __init__(
        self,
        bot: Bot,
        channel: discord.TextChannel,
        member: discord.Member,
        message: discord.Message = None,
        content: str = None,
        embed: discord.Embed = None,
        **kwargs,
    ):
        self.bot: Bot = bot
        self.channel: discord.TextChannel = channel
        self.member: discord.Member = member
        self.message: Optional[discord.Message] = message
        self.kwargs: dict = kwargs

        # these may be properties w/o setters, such as in the case of PaginatedMenu
        with suppress(AttributeError):
            self.content: Optional[str] = content
        with suppress(AttributeError):
            self.embed: Optional[discord.Embed] = embed

        self._react_task: Optional[asyncio.Task] = None

    @property
    def guild(self) -> discord.Guild:
        return self.channel.guild

    @property
    def emojis(self) -> List[Union[discord.Emoji, discord.PartialEmoji, str]]:
        return [x.emoji for x in self.actions]

    async def on_timeout(self) -> None:
        """Helper function called when the current menu times out.

        Can be overridden to perform a custom action. By default, this simply clears all reactions.
        """
        await self._handle_post_action(self.CLEAR_REACTIONS)

    def _reaction_check(
        self, event: asyncio.Event
    ) -> Callable[[discord.RawReactionActionEvent], bool]:
        def predicate(event_: discord.RawReactionActionEvent) -> bool:
            if event.is_set() or not self.message:
                # at this point we won't care about the result, so we're just going to return true
                # so that d.py has one less event listener to handle
                return True

            return (
                str(event_.emoji) in [str(x) for x in self.emojis]
                and event_.user_id == self.member.id
                and event_.message_id == self.message.id
            )

        return predicate

    async def _handle_post_action(self, post_action: str) -> None:
        if post_action == self.NO_ACTION:
            return

        me = self.guild.get_member(self.bot.user.id) if self.guild else self.bot.user
        can_manage_messages = self.guild and self.channel.permissions_for(me).manage_messages

        with suppress(discord.HTTPException):
            if post_action == self.DELETE_MESSAGE:
                await self.message.delete()
            if post_action == self.CLEAR_REACTIONS:
                if can_manage_messages:
                    await self.message.clear_reactions()
                else:
                    # discord.py doesn't add reaction objects to existing message objects,
                    # so we have to work around this by re-fetching the message from discord
                    try:
                        await self.__refetch()
                    except (discord.Forbidden, discord.NotFound):
                        # the message was either deleted or we don't have message history perms,
                        # so there's not much we can do here.
                        return

                    for react in self.message.reactions:
                        if react.me:
                            await self.message.remove_reaction(emoji=react.emoji, member=me)

    async def _add_reactions(self) -> None:
        try:
            for emoji in self.emojis:
                emoji_reaction: Optional[discord.Reaction] = discord.utils.get(
                    self.message.reactions, emoji=emoji
                )
                if emoji_reaction is None or not emoji_reaction.me:
                    await self.message.add_reaction(emoji)
        except (AttributeError, discord.NotFound, discord.Forbidden):
            pass
        except discord.HTTPException as e:
            log.exception("Failed to add an emoji to the current message", exc_info=e)

    async def __refetch(self):
        if self.message:
            self.message = await self.channel.fetch_message(self.message.id)

    async def update_message(self) -> None:
        """Update the menu message"""
        if not self.content and not self.embed:
            raise RuntimeError("Expected either message content or an embed, got neither")

        if self.message is None:
            self.message = await self.channel.send(content=self.content, embed=self.embed)
        else:
            try:
                await self.message.edit(content=self.content, embed=self.embed)
            except discord.NotFound:
                self.message = None
                await self.update_message()

    async def prompt(
        self, post_action: str = CLEAR_REACTIONS, timeout: Union[int, float, None] = 30
    ) -> None:
        """Begin the menu prompt

        Parameters
        ----------
        post_action: str
            The action to perform after the user interacts with the menu. This is disregarded
            if the action the user interacts with is marked to continue after use, or if the menu
            times out (see :func:`Menu.on_timeout`).

            Available actions are:

            * ``Menu.NO_ACTION``
            * ``Menu.CLEAR_REACTIONS`` (default)
            * ``Menu.DELETE_MESSAGE``
        timeout: Union[int, float, None]
            How long in seconds a user has to interact with the menu before it times out.
            May be set to :obj:`None` to never time out. Defaults to 30 seconds.

        Returns
        -------
        :obj:`None`
        """
        await self.update_message()
        # in case we didn't previously exit cleanly, but this menu instance is being reused for
        # whatever reason
        if self._react_task is not None:
            self._react_task.cancel()
        self._react_task = self.bot.loop.create_task(self._add_reactions())
        while True:
            # we're doing this so that we can get our listeners out of dpy after we've gotten
            # the event we care about, especially since we're listening for two events while only
            # acting on the first one we receive
            event = asyncio.Event()
            predicate = self._reaction_check(event)
            try:
                # we're listening for both add and remove events to avoid both having to
                # send an API request to remove reactions, and to avoid needing users
                # to remove and re-add their reaction for their interaction with the menu
                # to only be counted *once* if we can't remove reactions
                completed, _ = await asyncio.wait(
                    [
                        # long lived menu messages may be pushed out of d.py's message cache on
                        # very active guilds/bots, and to avoid this we have to listen for raw
                        # reaction events, instead of just regular reaction events. this is
                        # virtually unnecessary in most cases, but it can't hurt either way
                        self.bot.wait_for("raw_reaction_add", check=predicate),
                        self.bot.wait_for("raw_reaction_remove", check=predicate),
                    ],
                    loop=self.bot.loop,
                    timeout=timeout,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                # asyncio.wait doesn't raise a TimeoutError if times out, but instead returns
                # an empty completed list, so we have to special case this
                if not completed:
                    raise asyncio.TimeoutError
                reaction: discord.RawReactionActionEvent = completed.pop().result()
            except asyncio.TimeoutError:
                await self.on_timeout()
                break
            else:
                emoji = str(reaction.emoji)
                react_action: Action = discord.utils.find(
                    lambda x: str(x.emoji) == emoji, self.actions
                )
                post = react_action.post_action if react_action.continue_after_use else post_action
                if post != self.NO_ACTION:
                    # this is being done in a task as some post actions - namely clearing
                    # reactions w/o manage message permissions - might take a while to do
                    self.bot.loop.create_task(self._handle_post_action(post))

                await react_action(self)
                if not react_action.continue_after_use:
                    break
            finally:
                event.set()

        if self._react_task:
            self._react_task.cancel()
