Simple yet powerful reaction-based menu system

## Why use this over Red's menu utility?

This menu system effectively predates Red's built-in menu utility, and I haven't really found a reason to scrap it over Red's menu.

I also find it to be much more useful over Red's menu utility - both in terms of developer implementation, and usage on the user end.

- Adding *and* removing reactions are counted as interactions, instead of just adding reactions; this removes the need to remove reactions on each use of a menu,
  and also makes the menu much more usable in guilds where we don't have manage message permissions
- Menus are based on an action-based system, with each action being a separate class-level method decorated with the `action` function,
  instead of a bunch of functions in a dict, and as such are much cleaner and easier to understand at a glance

Additionally, this is meant to be portable with other discord.py bots, instead of being tied to Red in one way or another.

## Some examples

This menu system is designed to be much more understandable at a glance, and quicker to figure out and implement.

The following menu simply sends 'Hi!' as a response to a command, and waits for a `:wave:` reaction on that sent message before additionally sending `Hello {member}!`:

```python
from swift_libs.menus import Menu, action

class MyMenu(Menu):
    # The position of actions can be set by passing `position=x`, where `x` is an integer
    # Lower values are added first; refer to api docs for more usage info on actions
    @action("\N{WAVING HAND SIGN}")
    async def hello(self):
        await self.channel.send(f"Hello {self.member}!")

# actually implementing this function as a command is left as an exercise for the reader
async def my_command(ctx):
    await MyMenu(
      bot=ctx.bot, channel=ctx.channel, member=ctx.author, content="Hi!"
    ).prompt(post_action=Menu.DELETE_MESSAGE)
    # just sit back and relax - all of the boring work involved in menus is handled for you,
    # and you can focus on the rest of your code
```

And the same menu, but implemented with Red's menu utility:

```python
from contextlib import suppress
import discord
from redbot.core import commands
from redbot.core.utils.menus import menu

# out of all 7 variables being passed to this function, we're only using *two* of them!
async def hello(
    ctx: commands.Context,
    pages: list,
    controls: dict,
    message: discord.Message,
    page: int,
    timeout: float,
    emoji: str,
):
    with suppress(discord.NotFound):
        await message.delete()
    await message.channel.send(content=f"Hello {ctx.author}!")

async def my_command(ctx):
    await menu(ctx=ctx, pages=["Hi!"], controls={"\N{WAVING HAND SIGN}": hello})
```
