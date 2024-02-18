"""Assonant Instrument abstract class."""
from typing import Dict, List, Optional

from ..assonant_data_class import AssonantDataClass
from ..data_handlers import Axis, DataHandler


# TODO: Make this class abstract
class Instrument(AssonantDataClass):
    """Abstract class that creates the base common requirements to define an Assonant Instrument."""

    name: str
    positions: Optional[List[Axis]] = []
    fields: Optional[Dict[str, DataHandler]] = {}
