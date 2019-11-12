import logging

from redbot.core import Config

from .i18n import Translator

log = logging.getLogger("red.swift_libs")
translate = Translator(__file__, strict=True)

try:
    config = Config.get_conf(None, cog_name="swift_libs", identifier=413574221325)
except RuntimeError:
    # allow loading in an environment without red running, such as in the REPL or external scripts
    config = None
else:
    config.register_global(migrations={})
