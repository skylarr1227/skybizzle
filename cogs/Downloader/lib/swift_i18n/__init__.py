"""Simple yet intelligent translator based on ICU message formatting"""

# pylint:disable=wildcard-import
from .meta import __version__

try:
    from .core import *
    from .locale import *
    from .map import *
    from .humanize import *
except ImportError:
    # Probably pip accessing __version__
    pass
