"""Assonant Non-Instrument abstract class."""
from typing import Dict, Optional

from ..assonant_data_class import AssonantDataClass
from ..data_handlers import DataHandler


# TODO: Make this class abstract
class NonInstrument(AssonantDataClass):
    """Abstract class that creates the base common requirements to define an Assonant Non-Instrument."""

    fields: Optional[Dict[str, DataHandler]] = {}
