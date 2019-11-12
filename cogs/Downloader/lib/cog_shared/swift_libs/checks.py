"""Shared command checks"""
import importlib
import logging
from typing import List

import discord
from redbot.core import VersionInfo, version_info as _red_ver
from redbot.core.bot import Red
from redbot.core.commands import check
from redbot.core.errors import CogLoadError
from redbot.core.utils.chat_formatting import inline

from swift_i18n import Humanize
from . import version_info as _sl_ver
from ._internal import translate, log

__all__ = (
    "sl_version",
    "cogs_loaded",
    "hierarchy_allows",
    "try_import",
    "is_dev",
    "dev_mode",
    "red_version",
)


def sl_version(min_ver: str, cog: str = None):
    """Check if the version of swift_libs loaded matches the requested version

    Example
    -------
    >>> def setup(bot):
    ...     # On 1.0.x, this will raise a CogLoadError explaining how
    ...     # the bot owner can update their loaded swift_libs version.
    ...     sl_version("1.1.0")
    ...     # ...

    Arguments
    ----------
    min_ver: str
        The minimum swift_libs version your cog requires to load
    cog: Optional[str]
        Your cog's package name. If this is provided, your cog will be offered to be reloaded if
        ``[p]swiftlibs reload`` is invoked.
    """
    if VersionInfo.from_str(min_ver) > _sl_ver:
        if cog:
            # noinspection PyProtectedMember
            from .setup import require_update

            require_update.add(cog)

        raise CogLoadError(translate("checks.sl_outdated", current=_sl_ver, expected=min_ver))


def red_version(min_ver: str = None, max_ver: str = None) -> None:
    """Runtime Red version check

    This may be preferable if you'd like to check the bot's version independently of Downloader.

    Example
    -------
    >>> def setup(bot):
    ...     # If Red is on 3.1.0 or 3.1.1, this will raise a CogLoadError.
    ...     # Otherwise, this is comparable to a no-op.
    ...     # The above isn't applicable on 3.0.x, as simply importing swift_libs will raise
    ...     # a variety of import errors.
    ...     red_version("3.1.2")
    ...     # ...

    Parameters
    -----------
    min_ver: :class:`str`
        Minimum expected bot version
    max_ver: :class:`str`
        Maximum expected bot version; you shouldn't need to use this in most cases

    Raises
    ------
    CogLoadError
    """
    if not min_ver and not max_ver:
        raise RuntimeError("Neither minimum nor maximum versions were passed")

    if min_ver:
        min_ver = VersionInfo.from_str(min_ver)
    if max_ver:
        max_ver = VersionInfo.from_str(max_ver)
    if min_ver and max_ver and min_ver > max_ver:
        raise RuntimeError("Minimum version is greater than the maximum version")

    err = translate.lazy(
        "checks",
        (
            ("red_outdated_or_new" if min_ver != max_ver else "red_not_exact")
            if min_ver and max_ver
            else "red_outdated"
            if min_ver
            else "red_too_new"
        ),
        min=min_ver,
        max=max_ver,
        current=_red_ver,
    )

    if min_ver and min_ver > _red_ver:
        raise CogLoadError(str(err))
    if max_ver and max_ver < _red_ver:
        raise CogLoadError(str(err))


def try_import(*imports: str, extra: str = None) -> None:
    """Try to import required modules and raise an exception if any fail to import

    Keyword Arguments
    -----------------
    extra: str
        If this is provided, this will be logged as extra information alongside any
        import failures in the bot's logging.

    Raises
    -------
    CogLoadError
        Raised if one or more given imports fail to import
    """
    failed: List[str] = []
    for import_ in imports:
        try:
            importlib.import_module(import_)
        except Exception as e:  # pylint:disable=broad-except
            log.exception("Failed to import required library %r", import_, exc_info=e)
            failed.append(import_)

    if failed:
        if extra:
            log.warning("Extra information provided for the above import failures: %s", extra)

        raise CogLoadError(
            translate(
                "checks.import_failed", libs=Humanize([inline(x) for x in failed]), n=len(failed)
            )
        )


def cogs_loaded(*cogs):
    """Ensure that the cogs specified are loaded.

    Cog names are case sensitive.
    """
    return check(lambda ctx: not any([x for x in cogs if x not in ctx.bot.cogs]))


def dev_mode(bot: Red) -> bool:
    """Check if the bot is currently in development mode

    This function will return :obj:`True` if any of the following is true:

    * The Dev cog added by the --dev flag or a third-party lookalike is loaded
    * The ``red.swift_libs`` logger log level has been manually set to ``logging.DEBUG``
    * The ``red`` logger log level is set to ``logging.DEBUG`` with the --debug flag

    Otherwise, this will return :obj:`False`.

    .. note:: If you're looking for a command check variation of this, see: :func:`is_dev`

    Returns
    --------
    :class:`bool`
    """
    # check for the existence of the Dev cog added by the --dev flag, or a third-party lookalike
    if "Dev" in bot.cogs and hasattr(bot.get_cog("Dev"), "_eval"):
        return True

    # check for debug logging set by --debug or by modifying our or red's log level
    return 0 < log.getEffectiveLevel() <= logging.DEBUG


def is_dev():
    """Only allow command use in development mode

    .. important::
        **This is not a replacement for normal permission checks.** If your command warrants it,
        you should still use regular permission checks to ensure they are not usable by
        unauthorized users.

    .. seealso::
        * :func:`dev_mode`
    """
    return check(lambda ctx: dev_mode(ctx.bot))


async def hierarchy_allows(
    bot: Red, mod: discord.Member, member: discord.Member, *, allow_disable: bool = True
) -> bool:
    """Check if a guild's role hierarchy allows an action

    This check can be disabled on a per-guild basis with the Mod cog; however, this behaviour
    can be overridden with the `allow_disable` keyword argument.
    """
    if await bot.is_owner(mod):
        return True

    guild = mod.guild
    mod_cog = bot.get_cog("Mod")
    if (
        allow_disable
        and mod_cog is not None
        and not await mod_cog.settings.guild(guild).respect_hierarchy()
    ):
        return True

    return member != guild.owner and (mod == guild.owner or mod.top_role > member.top_role)
