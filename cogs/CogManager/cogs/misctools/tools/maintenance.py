from __future__ import annotations

import asyncio
import os
import shlex
import sys
from argparse import Namespace
from typing import Sequence
from typing import Union, Dict, Optional

from redbot.core import checks
from redbot.core.utils.chat_formatting import escape, pagify
from redbot.core.utils.chat_formatting import warning, info

from cog_shared.swift_libs.formatting import tick
from cog_shared.swift_libs.helpers import DefaultDict
from cog_shared.swift_libs.menus import Menu, action
from misctools import commands
from misctools.shared import Arguments, log, translate as translate_
from misctools.toolset import Toolset

translate = translate_.group("maintenance")
manager: Optional[MaintenanceManager] = None  # pylint:disable=used-before-assignment


class MaintenanceEnabled(commands.CheckFailure):
    pass


class MaintenanceManager:
    __slots__ = ("_bot", "cogs")

    def __init__(self):
        self._bot = False
        self.cogs: Dict[str, Union[bool, str]] = DefaultDict(False)

    @property
    def bot(self) -> Union[bool, str]:
        if "RED_MAINTENANCE" in os.environ:
            return self._bot if isinstance(self._bot, str) else True
        return self._bot

    @bot.setter
    def bot(self, value: Union[bool, str]):
        self._bot = value


class UpdateRedMenu(Menu):
    @property
    def content(self):
        return warning(
            translate("update_warning", command=" ".join(["python", *self.cli_args[1:]]))
        )

    @property
    def args(self) -> Namespace:
        return self.kwargs["args"]

    @property
    def package(self) -> str:
        if self.args.dev:
            branch = (
                "V3/develop"
                if not any([self.args.version, self.args.branch])
                else (self.args.version or self.args.branch)
            )
            package = (
                f"https://github.com/Cog-Creators/Red-DiscordBot/tarball/{branch}"
                f"#egg=Red-DiscordBot"
            )
        else:
            package = "red-discordbot"

        if self.args.version and not self.args.dev:
            package += f"=={self.args.version}"

        optionals = [
            x for x in ("mongo", "docs", "test", "postgres") if getattr(self.args, x) is True
        ]
        if optionals:
            package += "[{}]".format(", ".join(optionals))
        return package

    @property
    def cli_args(self) -> Sequence[str]:
        cli_args = [sys.executable, "-m", "pip", "install", "-U", self.package]
        if self.args.force:
            cli_args.insert(5, "--force-reinstall")
            cli_args.insert(5, "--no-cache-dir")
        return cli_args

    async def on_timeout(self):
        await self._handle_post_action(Menu.CLEAR_REACTIONS)
        await self.cancel()

    @action("\N{WHITE HEAVY CHECK MARK}", position=1)
    async def update_red(self):
        await self.message.edit(content=info(translate("updating")))
        async with self.channel.typing():
            log.info("Updating Red...")
            p = await asyncio.create_subprocess_exec(*self.cli_args, stdin=None, loop=self.bot.loop)
            await p.wait()

        # This is not a bug, nor unintended behaviour. `Message.delete` returns None,
        # which is what we're intending to set self.message to.
        self.message = await self.message.delete()
        await self.channel.send(translate("updated" if p.returncode == 0 else "update_failed"))

    @action("\N{CROSS MARK}", position=2)
    async def cancel(self):
        await self.message.edit(content=info(translate("update_cancelled")))


class Maintenance(Toolset, i18n=translate):
    async def toolset_setup(self):
        # This could probably be replaced with a class instance variable, but
        # doing this would require either just replacing the check on '[p]maintenance disable'
        # with an error response or doing equally weird shit, neither of which I'm
        # very fond of doing compared to this low effort solution.
        global manager
        manager = MaintenanceManager()

        self.register_defaults(maintenance__global=False, maintenance__cogs={})
        self.bot.add_check(self.global_check)
        self.bot.add_listener(self.error_listener, "on_command_error")

        data = await self.config.maintenance.all()
        # Convert older configurations
        if "enabled" in data:
            data["global"] = (
                data["message"] if data.get("message") and data["enabled"] else data["enabled"]
            )
            del data["enabled"]
            if "message" in data:
                del data["message"]
            await self.config.maintenance.set(data)

        manager.bot = data.get("global", False)
        manager.cogs.update(data.get("cogs", {}))

    def toolset_cleanup(self):
        self.bot.remove_check(self.global_check)
        self.bot.remove_listener(self.error_listener, "on_command_error")
        manager.bot = False
        manager.cogs.clear()

    async def global_check(self, ctx: commands.Context) -> bool:
        if await self.bot.is_owner(ctx.author):
            return True

        message: Optional[str] = None
        if manager.bot:
            message = (
                manager.bot if isinstance(manager.bot, str) else translate("currently_enabled")
            )
        elif ctx.cog:
            name = type(ctx.cog).__name__.lower()
            if manager.cogs[name] is not False:
                message = (
                    manager.cogs[name]
                    if isinstance(manager.cogs[name], str)
                    else translate("cog_enabled", cog=type(ctx.cog).__name__)
                )

        if message is not None:
            raise MaintenanceEnabled(escape(message, mass_mentions=True))
        return True

    @staticmethod
    async def error_listener(ctx: commands.Context, error: Exception):
        # This should be replaced in favour of UserFeedbackCheckFailure when
        # we bump the min version to 3.2.0 (or at least 3.1.3)
        if isinstance(error, MaintenanceEnabled):
            await ctx.send(error.args[0])

    @commands.group()
    @checks.is_owner()
    @translate.command("help.maintenance")
    async def maintenance(self, ctx: commands.Context):
        pass

    @maintenance.command(name="enable")
    @translate.command("help.maintenance_enable")
    async def maintenance_enable(self, ctx: commands.Context, *, message: str = None):
        manager.bot = message or True
        await self.config.maintenance.set_raw("global", value=message or True)
        await ctx.send(tick(translate("enabled")))

    @maintenance.command(name="disable")
    @commands.check(lambda ctx: manager.bot is not False)
    @translate.command("help.maintenance_disable")
    async def maintenance_disable(self, ctx: commands.Context):
        if os.environ.get("RED_MAINTENANCE"):
            await ctx.send(warning(translate("set_by_env")))
            return

        manager.bot = False
        await self.config.maintenance.set_raw("global", value=False)
        await ctx.send(tick(translate("disabled")))

    @maintenance.command(name="cog", usage="(enable|disable) <cog> [message]")
    @translate.command("help.maintenance_cog")
    async def maintenance_cog(
        self, ctx: commands.Context, status: str, cog: str, *, message: str = None
    ):
        status = status in ("enabled", "enable", "1", "yes", "true", "on")
        cog = next(iter(x.lower() for x in self.bot.cogs.keys() if x.lower() == cog.lower()), None)
        if cog is None:
            await ctx.send(translate("no_such_cog"))
            return

        manager.cogs[cog] = message if message and status else status
        if not status:
            await self.config.maintenance.cogs.set_raw(cog, value=False)
        else:
            await self.config.maintenance.cogs.set_raw(cog, value=message or True)
        await ctx.tick()

    @maintenance.command(name="status", aliases=["info"])
    @translate.command("help.maintenance_info")
    async def maintenance_info(self, ctx: commands.Context):
        cogs = {
            next(x for x in self.bot.cogs if x.lower() == k): v
            if isinstance(v, str)
            else translate("no_message")
            for k, v in manager.cogs.items()
            if v and any(x.lower() == k for x in self.bot.cogs)
        }

        message = [translate("bot_maintenance", status="true" if manager.bot else "false")]
        if manager.bot and isinstance(manager.bot, str):
            message.append(translate("message", message=manager.bot))
        message.append("")

        if cogs:
            message.append(translate("cogs_in_maintenance", count=len(cogs)))
            for cog, msg in cogs.items():
                message.append(f"    \N{BULLET} **`{cog}`** \N{EM DASH} {msg}")

        for page in pagify(info("\n".join(message))):
            await ctx.send(page)

    @commands.command()
    @checks.is_owner()
    @translate.command("help.updatered")
    async def updatered(self, ctx: commands.Context, *, args: str = ""):
        parser = Arguments(add_help=False)
        parser.add_argument("-d", "--dev", "--git", action="store_true")
        parser.add_argument("-m", "--mongo", "--mongodb", action="store_true")
        parser.add_argument("-p", "--postgres", "--psql", action="store_true")
        parser.add_argument("--docs", action="store_true")
        parser.add_argument("--test", action="store_true")
        parser.add_argument("-V", "--version", type=str, default=None)
        parser.add_argument("--branch", type=str, default=None)
        parser.add_argument("--force", action="store_true")
        args = parser.parse_args(shlex.split(args))

        await UpdateRedMenu(bot=ctx.bot, channel=ctx.channel, member=ctx.author, args=args).prompt(
            post_action=Menu.CLEAR_REACTIONS
        )
