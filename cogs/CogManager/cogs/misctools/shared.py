import argparse
import logging

from redbot.core import commands, Config

from cog_shared.swift_libs.i18n import Translator

translate = Translator(__file__)
log = logging.getLogger("red.misctools")

try:
    config = Config.get_conf(
        None, cog_name="MiscTools", identifier=421412412, force_registration=True
    )
    config.register_global(toolsets=[])
except RuntimeError:
    config = None


class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise commands.BadArgument(message)
