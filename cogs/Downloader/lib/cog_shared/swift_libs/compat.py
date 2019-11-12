from redbot.core.commands import Cog

__all__ = ("listener",)

if hasattr(Cog, "listener"):
    listener = Cog.listener
else:

    # noinspection PyUnusedLocal
    def listener(name=None):
        return lambda f: f
