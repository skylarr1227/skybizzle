from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Awaitable, List

from ._internal import log, config

__all__ = ("Schema",)


class Schema:
    """Cog migrations class

    This internally versions your cog with a version number based on either the highest version
    you've given a migration, or the total amount of migrations you've created for this schema.

    Arguments
    ---------
    cog: str
        The name to use for storing your cog's schema version
    skip_first: bool
        If this is :obj:`False`, all migrations will be ran even if the cog was first loaded
        after such migrations were added.
    """

    __slots__ = ("cog", "skip_first", "migrations")

    def __init__(self, cog: str, skip_first: bool = True):
        self.cog = cog
        self.skip_first = skip_first
        self.migrations: List[Migration] = []

    def __repr__(self):
        return f"<Schema cog={self.cog!r} version={self.version!r} migrations={self.migrations!r}>"

    @classmethod
    async def mark(cls, cog: str):
        """Mark a cog as installed by setting its schema version to 0 in Config

        This is primarily useful if you intend to possibly use migrations in the future,
        but currently have nothing to be migrated.
        """
        if await config.get_raw("migrations", cog, default=None) is None:
            log.debug("Marking cog %s as at migration 0.", cog)
            await config.set_raw("migrations", cog, value=0)

    @property
    def version(self):
        """The current cog schema version"""
        return max([*[x.version for x in self.migrations], 0])

    def migration(self, description: str = None, **kwargs) -> Callable[[Callable], Migration]:
        """Create a schema migration

        Keyword Arguments
        -----------------
        version: Optional[int]
            Optional version number to give this migration; defaults to ``Schema.version + 1``
        description: Optional[str]
            Optional description to give this schema. Used in logging when your cog's config schema
            is updated.
        silent: bool
            If this is :obj:`True`, this migration will not log anything when invoked.
        """
        kwargs.setdefault("version", self.version + 1)
        kwargs.setdefault("description", description)

        def wrapper(func):
            migration = Migration(callable=func, **kwargs)
            self.migrations.append(migration)
            return migration

        return wrapper

    async def run(self, *args, **kwargs):
        """Run applicable schema migrations"""
        ver = await config.get_raw("migrations", self.cog, default=None)
        if ver is None:
            await config.set_raw("migrations", self.cog, value=self.version)
            if self.skip_first:
                log.debug("Skipping first migration invoke for cog %s", self.cog)
                return
            ver = 0
        if ver >= self.version:
            log.debug(
                "Cog %s config is at schema version %s and we're at %s, nothing to do.",
                self.cog,
                ver,
                self.version,
            )
            return
        for update in range(ver, self.version):
            migration = self.migrations[update]
            if not migration.silent:
                log.info(
                    "Updating schema for cog %s to version %s (%s)",
                    self.cog,
                    migration.version,
                    migration.description or "no description provided",
                )
            try:
                await migration.callable(*args, **kwargs)
            except Exception as e:  # pylint:disable=broad-except
                log.exception("Failed to run migration for schema version %s", update, exc_info=e)
        await config.set_raw("migrations", self.cog, value=self.version)


@dataclass(frozen=True, eq=False)
class Migration:
    callable: Callable[..., Awaitable[None]]
    version: int
    description: Optional[str] = None
    silent: bool = False

    def __eq__(self, other):
        return (
            isinstance(other, type(self))
            and self.callable is other.callable
            and self.version == other.version
        )
