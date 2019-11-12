import os
from typing import Dict

import discord

from swift_i18n.util import LazyStr
from ._internal import translate

__all__ = ("permission_translations", "format_permission")
#: A mapping of :class:`discord.Permissions` keys to
#: :class:`~swift_libs.translations.LazyStr` values
permission_translations: Dict[str, LazyStr] = {}

if "BUILDING_DOCS" not in os.environ:
    for k, _ in discord.Permissions():
        permission_translations[k] = translate.lazy(
            "permissions", k, default=k.replace("_", " ").title()
        )


def format_permission(perm: str):
    """Try to translate a permission from :obj:`permission_translations`

    If the permission given is not in the configured translation locale(s), this falls back to
    replacing underscores with spaces and title-casing the given string.
    """
    return str(permission_translations.get(perm, perm.replace("_", " ").title()))
