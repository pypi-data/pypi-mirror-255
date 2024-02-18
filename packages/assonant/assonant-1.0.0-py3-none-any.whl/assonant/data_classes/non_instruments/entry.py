"""Assonant Entry data class."""
from typing import List, Optional

from ..instruments import Instrument
from ..types import ScopeType
from .non_instrument import NonInstrument
from .sample import Sample


class Entry(NonInstrument):
    """Data classes that wraps data into a logical/temporal scope related to the experiment.

    Entries are used to group and represent data in a defined temporal/logical scope of the
    experiment, which is directly define by the field "scope_type". e.g: calibration, pre-exposition.
    """

    scope_type: ScopeType
    instruments: Optional[List[Instrument]] = []
    sample: Optional[Sample] = None
