from typing import Union

from discord.abc import Snowflake
from redbot.core import Config

# noinspection PyProtectedMember
from redbot.core.config import Group

from .consts import undefined

__all__ = ("cfg_scope", "try_set")
DEFAULT_SCOPES = (
    Config.GLOBAL,
    Config.GUILD,
    Config.MEMBER,
    Config.USER,
    Config.ROLE,
    Config.CHANNEL,
)


def cfg_scope(cfg: Config, scope: str, *identifiers):
    """Safely retrieve a base config Group with unknown scopes

    This works around default scopes not being able to be retrieved with
    :attr:`redbot.core.config.Config.custom` as of Red 3.1.
    """
    if scope in DEFAULT_SCOPES:
        if scope == Config.GLOBAL:
            return cfg
        elif scope == Config.CHANNEL:
            return cfg.channel(*identifiers)
        else:
            return getattr(cfg, scope.lower())(*identifiers)
    return cfg.custom(
        scope, *[getattr(x, "id") if isinstance(x, Snowflake) else x for x in identifiers]
    )


async def try_set(cfg: Union[Group, Config], *keys, default):
    """Try to get a value from :class:`~redbot.core.config.Config`, or set it if it doesn't exist

    This differs from the ``default`` kwarg available in :func:`~redbot.core.config.Value.get_raw`
    as this sets the value in Config to the given default if it doesn't exist, which makes this
    effectively similar to ``setdefault`` on a :class:`dict`.

    Parameters
    ----------
    cfg: Union[:class:`~redbot.core.config.Group`, :class:`~redbot.core.config.Config`]
        The config group to try to use
    *keys: str
        Config key(s) to use
    default: Any
        The value to set if the given config key doesn't exist
    """
    try:
        value = await cfg.get_raw(*keys, default=undefined)
        if value is undefined:
            raise ValueError
    except (ValueError, KeyError):
        await cfg.set_raw(*keys, value=default)
        return default
    else:
        return value
