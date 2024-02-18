"""Assonant data classes - Instruments submodule.

Data classes responsible for grouping data related to instrumental data
"""

from .bvs import BVS
from .detector import Detector
from .instrument import Instrument
from .mirror import Mirror
from .monochromator import Monochromator
from .slit import Slit

__all__ = [
    "Instrument",
    "Detector",
    "Mirror",
    "Monochromator",
    "Slit",
    "BVS",
]
