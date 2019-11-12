from os import environ as _environ

try:
    from redbot.core.config import Config as _Config
except ImportError:
    _Config = None

__all__ = ("undefined", "MONGODB")

#: This will be :obj:`True` if the MongoDB Config driver is currently in use, :obj:`False` otherwise
MONGODB: bool = ...

# Deprecated constants; kept for backwards compatibility
NEW_MONGODB = True


if "BUILDING_DOCS" not in _environ and _Config is not None:
    try:
        MONGODB = (
            type(
                _Config.get_conf(None, cog_name="swift_libs", identifier=413574221325).driver
            ).__name__
            == "Mongo"
        )
    except RuntimeError:
        # we're running in a headless environment such as the repl or in scripts
        MONGODB = False


# noinspection PyPep8Naming
class undefined:
    def __repr__(self):
        return f"<{self.__module__}.undefined>"

    def __bool__(self):
        return False


#: Sentinel placeholder object to use where using :obj:`None` as a default would be ambiguous.
undefined = undefined()
