
"""
This module is the entry point for the mtbp3 package.
It imports all the functions and classes from the util module.
"""

from .util import *

from importlib.metadata import version
__version__ = version(__package__)

import os

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_data(path):
    return os.path.join(_ROOT, 'data', path)

