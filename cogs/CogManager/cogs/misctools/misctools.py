from typing import Type, List, Union

import discord
from redbot.core import commands, checks
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import pagify, inline, bold, box

from misctools.shared import translate, log, config
from misctools.tools import toolsets
from misctools.toolset import Toolset
from swift_i18n import Humanize
from swift_i18n.util import LazyStr


class UnknownToolset(KeyError):
    pass


class NotLoaded(KeyError):
    pass


class AlreadyLoaded(KeyError):
    pass


class InternalLoadError(Exception):
    def __init__(self, translated: LazyStr, untranslated: str):
        self.translated = translated
        self.untranslated = untranslated


@translate.cog("help.cog")
class MiscTools(commands.Cog):
    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.loaded: List[Toolset] = []
        self._update_commands()

    def cog_unload(self):
        log.debug("MiscTools is being unloaded, tearing down loaded toolsets")
        for toolset in self.loaded:
            try:
                self.unload(toolset)
            except Exception as e:  # pylint:disable=broad-except
                log.exception("Failed to unload toolset %r", toolset.__class__.__name__, exc_info=e)

    async def bootstrap(self):
        to_load = await config.toolsets()
        loaded = []
        for name in to_load:
            try:
                await self.load(name)
            except AlreadyLoaded:
                log.warning(
                    "Toolset %r is referenced more than once in the bot's configuration", name
                )
            except UnknownToolset:
                log.warning("Failed to find a toolset with the name %r - skipping", name)
                async with config.toolsets() as configured:
                    configured.remove(name)
            except InternalLoadError as e:
                log.error("Could not load toolset %r: %s", name, e.untranslated)
            # Treat any other exception as a fatal exception and bail
            except Exception as e:
                self.cog_unload()
                raise RuntimeError(f"Failed to load toolset {name!r}") from e
            else:
                loaded.append(name.lower())
        if loaded:
            log.info("Loaded toolsets: %s", ", ".join(loaded))

    @staticmethod
    def find(toolset: str):
        try:
            return next(x for x in toolsets if x.__name__.lower() == toolset.lower())
        except StopIteration:
            raise UnknownToolset(toolset)

    def ensure_loadable(self, toolset: Union[Type[Toolset], str]):
        if isinstance(toolset, str):
            toolset = self.find(toolset)
        if any(type(x) is toolset for x in self.loaded):
            raise AlreadyLoaded(toolset)

        # Better feedback for command conflicts instead of just outright failing to load
        for command in toolset.__commands__:
            if self.bot.get_command(command.qualified_name):
                if any(command.qualified_name.startswith(x) for x in toolset.conflict_ok):
                    continue
                conflicts_with = self.bot.get_command(command.qualified_name).cog
                conflicts_with = getattr(conflicts_with, "qualified_name", conflicts_with)
                raise InternalLoadError(
                    translate.lazy(
                        "command_conflict",
                        toolset=toolset.__name__,
                        command=command.qualified_name,
                        cog=conflicts_with,
                    ),
                    f"Command {command.qualified_name!r} conflicts with a command with the"
                    f" same name from cog {conflicts_with!r}",
                )

    async def load(self, toolset: Union[Type[Toolset], str]):
        self.ensure_loadable(toolset)
        if isinstance(toolset, str):
            toolset = self.find(toolset)
        toolset = toolset(self.bot)

        try:
            await discord.utils.maybe_coroutine(toolset.toolset_before_setup)

            for command in toolset.__commands__:
                log.debug("Setting up command %r", command.qualified_name)
                # pylint:disable=protected-access
                command._actual_self = toolset
                command._appear_from = self
                # pylint:enable=protected-access
                if not command.parent:
                    self.bot.add_command(command)
                self.bot.dispatch("command_add", command)

            await discord.utils.maybe_coroutine(toolset.toolset_setup)
        except Exception:
            self.unload(toolset)
            raise

        self.loaded.append(toolset)
        self._update_commands()

    def unload(self, toolset: Union[Type[Toolset], str, Toolset]):
        if isinstance(toolset, str):
            toolset = self.find(toolset)
        if isinstance(toolset, Toolset) and not isinstance(toolset, type):
            toolset = type(toolset)
        try:
            toolset = next(x for x in self.loaded if type(x) is toolset)
        except StopIteration:
            raise NotLoaded(toolset if isinstance(toolset, str) else toolset.__name__)

        for command in list(self.bot.all_commands.values()):
            if (
                command.cog is self
                and (not command.parent or isinstance(command.parent, Red))
                and any(x.qualified_name == command.qualified_name for x in toolset.__commands__)
            ):
                self.bot.remove_command(command.qualified_name)

        toolset.toolset_cleanup()
        self.loaded.remove(toolset)
        self._update_commands()

    def _update_commands(self):
        # If you're here to find out how we're adding commands to the MiscTools command group
        # despite the commands being in a different class, see `commands.py`. You really
        # shouldn't attempt this however, since what we're doing requires mucking with
        # discord.py classes.
        self.__cog_commands__ = self.all_commands()

    def all_commands(self):
        cmds = [x for x in self.__class__.__dict__.values() if isinstance(x, commands.Command)]
        for toolset in self.loaded:
            cmds.extend(toolset.__commands__)
        return cmds

    @commands.group(aliases=["tools", "toolset"])
    @checks.is_owner()
    @translate.command("help.misctools")
    async def misctools(self, ctx: commands.Context):
        pass

    @misctools.command(name="info", aliases=["show", "details"])
    @translate.command("help.info")
    async def misctools_info(self, ctx: commands.Context, toolset: str):
        try:
            toolset = self.find(toolset)
        except UnknownToolset:
            await ctx.send(translate("toolset_not_found", set=toolset))
            return

        embed = discord.Embed(
            colour=await ctx.embed_colour(), description=str(toolset.tool_description)
        )
        embed.set_author(
            name=translate("toolset_info"), icon_url=self.bot.user.avatar_url_as(format="png")
        )
        embed.add_field(
            name=translate("commands"),
            value="\n".join(
                [
                    f"**{ctx.prefix}{x.qualified_name}** \N{EM DASH} {x.short_doc!s}"
                    for x in toolset.__commands__
                    if (
                        (not x.parent or isinstance(x.parent, Red))
                        and not x.hidden
                        and await x.can_run(ctx)
                    )
                ]
            ),
        )
        await ctx.send(embed=embed)

    @misctools.command(name="list")
    @translate.command("help.list")
    async def misctools_list(self, ctx: commands.Context):
        unloaded = [x for x in set(toolsets) - {type(x) for x in self.loaded} if not x.hidden]
        embeds = await ctx.embed_requested()
        if self.loaded:
            if embeds:
                await ctx.send(
                    embed=discord.Embed(
                        colour=discord.Colour.green(),
                        title=bold(translate("loaded_toolsets", count=len(self.loaded))),
                        description=", ".join([type(x).__name__.lower() for x in self.loaded]),
                    )
                )
            else:
                await ctx.send(
                    box(
                        "{}\n\n+ {}".format(
                            translate("loaded_toolsets", count=len(self.loaded)),
                            ", ".join([type(x).__name__.lower() for x in self.loaded]),
                        ),
                        lang="diff",
                    )
                )
        if unloaded:
            if embeds:
                await ctx.send(
                    embed=discord.Embed(
                        colour=discord.Colour.red(),
                        title=bold(translate("unloaded_toolsets", count=len(unloaded))),
                        description=", ".join([x.__name__.lower() for x in unloaded]),
                    )
                )
            else:
                await ctx.send(
                    box(
                        "{}\n\n- {}".format(
                            translate("unloaded_toolsets", count=len(unloaded)),
                            ", ".join([x.__name__.lower() for x in unloaded]),
                        ),
                        lang="diff",
                    )
                )

    @misctools.command(name="load", aliases=["enable", "add"], usage="<toolsets...>")
    @translate.command("help.load")
    async def misctools_load(self, ctx: commands.Context, *toolsets_: str):
        if not toolsets_:
            await ctx.send_help()
            return

        loaded = []
        output = []

        for toolset in toolsets_:
            try:
                await self.load(toolset)
            except AlreadyLoaded:
                output.append(translate("toolset_already_loaded", set=toolset))
            except UnknownToolset:
                output.append(translate("toolset_not_found", set=toolset))
            except InternalLoadError as e:
                output.append(str(e.translated))
            except Exception as e:  # pylint:disable=broad-except
                log.exception("Failed to load toolset %r", toolset.lower(), exc_info=e)
                output.append(translate("toolset_errored", set=toolset))
            else:
                async with config.toolsets() as toolsets__:
                    ts = self.find(toolset).__name__
                    if ts not in toolsets__:
                        toolsets__.append(ts)
                loaded.append(toolset)

        if loaded:
            output.append(
                translate(
                    "toolset_loaded", count=len(loaded), sets=Humanize([inline(x) for x in loaded])
                )
            )

        for page in pagify("\n".join(output)):
            await ctx.send(page)

    @misctools.command(name="unload", aliases=["disable", "remove"], usage="<toolsets...>")
    @translate.command("help.unload")
    async def misctools_unload(self, ctx: commands.Context, *toolsets_: str):
        if not toolsets_:
            await ctx.send_help()
            return

        unloaded = []
        output = []

        for toolset in toolsets_:
            try:
                self.unload(toolset)
            except UnknownToolset:
                output.append(translate("toolset_not_found", set=toolset))
            except NotLoaded:
                output.append(translate("toolset_already_unloaded", set=toolset))
            else:
                unloaded.append(toolset)
                async with config.toolsets() as toolsets__:
                    for ts in toolsets__.copy():
                        if ts.lower() == toolset.lower():
                            toolsets__.remove(ts)

        if unloaded:
            output.append(
                translate(
                    "toolset_unloaded",
                    count=len(unloaded),
                    sets=Humanize([inline(x) for x in unloaded]),
                )
            )

        for page in pagify("\n".join(output)):
            await ctx.send(page)
