from typing import Dict, Any, Optional, ClassVar, List

from redbot.core import Config, commands
from redbot.core.bot import Red

from misctools.commands import _CommandMixin
from misctools.shared import config, translate
from swift_i18n.util import LazyStr

defaults: Dict[str, Dict[str, Any]] = {Config.GLOBAL: {"toolsets": []}}


def rebuild_defaults() -> None:
    for scope, values in defaults.items():
        config.register_custom(scope, **values)


class Toolset:
    tool_description: ClassVar[Optional[LazyStr]] = None
    # Unloaded hidden toolsets won't be listed in '[p]misctools list'; loaded toolsets
    # will still be be listed regardless of this value.
    hidden: ClassVar[bool] = False
    conflict_ok: ClassVar[List[str]] = []

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = config

    def __init_subclass__(cls, **kwargs):
        not_using_mt = [
            x
            for x in cls.__dict__.values()
            if isinstance(x, commands.Command) and not isinstance(x, _CommandMixin)
        ]
        if any(not_using_mt):
            raise RuntimeError(
                "One or more of this toolset's commands do not use the MiscTools command classes"
            )
        if "i18n" in kwargs and "__description__" in kwargs["i18n"]:
            kwargs.setdefault("description", kwargs["i18n"].lazy("__description__"))
        cls.tool_description = kwargs.get("description", translate.lazy("no_description"))
        translator = kwargs.get("i18n", None)
        (translator or translate).attach_to_commands(cls)
        cls.__commands__ = [x for x in cls.__dict__.values() if isinstance(x, commands.Command)]

    @staticmethod
    def register_defaults(scope: str = Config.GLOBAL, **kwargs):
        if scope not in defaults:
            defaults[scope] = {}
        defaults[scope].update(kwargs)
        rebuild_defaults()

    def toolset_before_setup(self):
        """Hook called before your toolset's commands are loaded

        By default, this method is a no-op.

        This method may be async.
        """
        pass

    def toolset_setup(self):
        """Hook called after your toolset's commands are loaded

        By default, this calls your __tool_setup method if it exists.

        This method may be async.
        """
        func = getattr(self, f"_{self.__class__.__name__}__tool_setup", None)
        if func:
            return func()

    def toolset_cleanup(self):
        """Hook called after your toolset's commands are unloaded

        By default, this calls your __tool_cleanup method if it exists.

        This method must not be async.
        """
        func = getattr(self, f"_{self.__class__.__name__}__tool_cleanup", None)
        if func:
            return func()
