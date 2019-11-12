from __future__ import annotations

from difflib import Differ, SequenceMatcher
from typing import Sequence

import discord

from .consts import undefined

__all__ = (
    "tick",
    "cross",
    "index",
    "mention",
    "SimpleDiffer",
    "CloneableEmbed",
    "link",
    "message_link",
)


class CloneableEmbed(discord.Embed):
    def clone(self) -> CloneableEmbed:
        """Clone the current embed"""
        return self.from_dict(self.to_dict())


def mention(item) -> str:
    """Mention resolver w/ special handling for the @everyone role"""
    if isinstance(item, discord.Role):
        return item.mention if not item.is_default() else item.name
    else:
        return item.mention


def index(seq: Sequence, item) -> str:
    """Returns a zero-padded index for `item`"""
    if isinstance(seq, dict):
        seq = list(seq.values())
    index_ = str(seq.index(item) + 1)
    return index_.zfill(len(index_))


def link(text: str, url: str) -> str:
    """Create a markdown hyperlink

    .. important:: The returned hyperlink is only usable in embeds.
    """
    return "[{}]({})".format(text.replace("]", "\\]"), url.replace(")", "\\)"))


def message_link(message: discord.Message, *, text: str = undefined) -> str:
    """Create a message hyperlink

    .. important:: The returned hyperlink is only usable in embeds.
    """
    from ._internal import translate

    return link(text or translate("formatting.jump_to_message"), message.jump_url)


def tick(text: str) -> str:
    """Return `text` with a check mark emoji prepended"""
    return f"\N{WHITE HEAVY CHECK MARK} {text}"


def cross(text: str) -> str:
    """Return `text` with a cross mark emoji prepended"""
    return f"\N{CROSS MARK} {text}"


class SimpleDiffer(Differ):
    """A variation of Differ without a fancy replace, somewhat similarly to git diffs"""

    def compare(self, a, b):
        r"""Compare two sequences of lines; generate the resulting delta.

        Each sequence must contain individual single-line strings ending with
        newlines. Such sequences can be obtained from the `readlines()` method
        of file-like objects.  The delta generated also consists of newline-
        terminated strings, ready to be printed as-is via the writeline()
        method of a file-like object.

        Example
        -------

        >>> print(''.join(SimpleDiffer().compare(
        ...     'one\ntwo\nthree\n'.splitlines(True),
        ...     'ore\ntree\nemu\n'.splitlines(True))),
        ...     end="",
        ... )
        - one
        + ore
        - two
        - three
        + tree
        + emu
        """
        cruncher = SequenceMatcher(self.linejunk, a, b)
        for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
            if tag == "replace":
                yield from self._dump("-", a, alo, ahi)
                g = self._dump("+", b, blo, bhi)
            elif tag == "delete":
                g = self._dump("-", a, alo, ahi)
            elif tag == "insert":
                g = self._dump("+", b, blo, bhi)
            elif tag == "equal":
                g = self._dump(" ", a, alo, ahi)
            else:
                raise ValueError(f"unknown tag {tag!r}")

            yield from g
