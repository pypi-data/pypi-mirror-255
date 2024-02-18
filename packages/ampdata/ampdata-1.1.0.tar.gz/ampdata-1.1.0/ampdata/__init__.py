#
# Ampiato AmpData API access library
#
import os
from .session import Session  # noqa: F401
from . import auth, curves, events, session, util  # noqa: F401

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "VERSION")) as fv:
    VERSION = __version__ = fv.read().strip()
