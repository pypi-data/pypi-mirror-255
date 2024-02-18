# -*- coding: utf-8 -*-

__uri__ = "https://pylick.readthedocs.io"
__author__ = "Nicola Borghi, Michele Moresco, Salvatore Quai"
__email__ = "nicola.borghi6@unibo.it,  michele.moresco@unibo.it"
__license__ = "GPLv3"
__description__ = "Python tool to measure spectral features"


from .__version__ import __version__  # isort:skip
from . import analysis
from . import indices
from . import io
from . import measurement
from . import plot

__all__ = [
    "analysis",
    "indices",
    "io",
    "measurement",
    "plot",
]
