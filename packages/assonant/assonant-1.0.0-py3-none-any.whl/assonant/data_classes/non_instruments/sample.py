"""Assonant Sample data class."""
from typing import List, Optional

from ..data_handlers import Axis
from .non_instrument import NonInstrument


class Sample(NonInstrument):
    """Data class to handle all data required to define a sample."""

    name: str
    positions: Optional[List[Axis]] = []
