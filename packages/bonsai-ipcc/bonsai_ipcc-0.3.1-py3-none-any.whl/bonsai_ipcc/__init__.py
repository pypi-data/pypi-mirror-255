# NOTE: Do not edit here
# Dependencies for __init__ file, d
import logging
import sys
from os import listdir
from os.path import dirname
from pathlib import Path

from .core import IPCC
from .log_setup import setup_logger

# setup the default logger
setup_logger()

# NOTE: Do not edit from here downward
# Create package version number from git tag
if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover


try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError, dist_name, sys, logging


# Remove files and folders starting with underscore from dir()
PATH = Path(dirname(__file__))
for f in listdir(PATH):
    if f[0] == "_":
        STEM = Path(f).stem
        exec(f"from . import {STEM}")
        exec(f"del {STEM}")

del (
    listdir,
    dirname,
    Path,
    PATH,
    STEM,
    f,
)
