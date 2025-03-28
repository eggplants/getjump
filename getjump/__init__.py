""".. include:: ../README.md"""

import importlib.metadata

from .getjump import VALID_HOSTS, GetJump

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ("VALID_HOSTS", "GetJump")
